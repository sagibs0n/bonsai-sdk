# Copyright (C) 2018 Bonsai, Inc.

from urllib.parse import urljoin, urlparse, urlunparse

import requests

from bonsai_ai.common.utils import get_user_info
from bonsai_ai.logger import Logger
from bonsai_ai.brain_api import BrainAPI
from .aria_writer import AriaWriter

log = Logger()

# constants for brain state
INKLING_LOADED = 'Inkling Loaded'
NOT_STARTED = 'Not Started'
STARTING = 'Starting'
IN_PROGRESS = 'In Progress'
STOPPED = 'Stopped'
COMPLETED = 'Completed'
FINISHING = 'Finishing'


class Brain(object):
    """
    Manages communication with the BRAIN on the server.

    This class can be used to introspect information about a BRAIN on the
    server and is used to query status and other properties.

    Attributes:
        config:         The configuration object used to connect to this BRAIN.
        description:    A user generated description of this BRAIN.
        exists:         Whether this BRAIN exists on the server.
        name:           The name of this BRAIN.
        ready:          Whether this BRAIN is ready for training.
        state:          Current state of this BRAIN on the server.
        version:        The currently selected version of the BRAIN.
        latest_version: The latest version of the BRAIN.

    Example:
        import sys, bonsai_ai
        config = bonsai_ai.Config(sys.argv)
        brain = bonsai_ai.Brain(config)
        print(brain)

    """
    def __init__(self, config, name=None):
        """
        Construct Brain object by passing in a Config object with an
        optional name argument.

        Arguments:
            config: A configuration used to connect to the BRAIN.
            name:   The name of the BRAIN to connect to.
        """
        self._config = config
        self._api = BrainAPI(config, config.network_timeout)
        self._timeout = self.config.network_timeout
        self.description = None
        self.name = name if name else self.config.brain
        self._status = None
        self._info = None
        self._state = None
        self._sims = None
        self.latest_version = None
        self._user_info = get_user_info()
        self._aria_writer = AriaWriter(
            cluster_url=config.url,
            disable_telemetry=config.disable_telemetry
        )
        self.update()

    def __repr__(self):
        return '{{'\
            'name: {self.name!r}, ' \
            'description: {self.description!r}, ' \
            'latest_version: {self.latest_version!r}, ' \
            'config: {self.config!r}' \
            '}}'.format(self=self)

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config
        self._api = BrainAPI(config, config.network_timeout)

    def _brain_url(self):
        """ Utility function to obtain brain url from config.
            Example: http://localhost:5000/v1/nav/brain3 """
        url_base = self.config.url
        url_path = '/v1/{user}/{brain}'.format(
            user=self.config.username,
            brain=self.name
        )
        return urljoin(url_base, url_path)

    def _websocket_url(self):
        # Grab api url and split it
        api_url = self._brain_url()
        api_url = urlparse(api_url)

        # Replace the scheme with ws or wss depending on protocol
        if api_url.scheme == 'http':
            split_ws_url = api_url._replace(scheme='ws')
        elif api_url.scheme == 'https':
            split_ws_url = api_url._replace(scheme='wss')
        else:
            split_ws_url = api_url
        ws_url = urlunparse(split_ws_url)
        return ws_url

    def _prediction_url(self):
        """ Utility function to obtain prediction url from config """
        return '{ws_url}/{version}/predictions/ws'.format(
            ws_url=self._websocket_url(),
            version=self.version)

    def _simulation_url(self):
        """ Returns simulation url """
        return '{}/sims/ws'.format(self._websocket_url())

    def _proxy_header(self):
        """ Utility function to obtain proxy that is sent with requests """
        if self.config.proxy:
            url_components = urlparse(self.config.proxy)
            proxy_dict = {url_components.scheme: self.config.proxy}
            return proxy_dict
        else:
            return None

    def update(self):
        """
        Refreshes description, status, and other information with the
        current state of the BRAIN on the server. Called by default when
        constructing a new Brain object.
        """
        try:
            log.brain('Getting {} info...'.format(self.name))
            self._info = self._api.get_brain_info(self.name)
            if self._info['versions']:
                self.latest_version = self._info['versions'][0]['version']
            else:
                self.latest_version = 0

            log.brain('Getting {} info...'.format(self.name))
            self._status = self._api.get_brain_status(self.name)

            log.brain('Getting {} sims...'.format(self.name))
            self._sims = self._api.get_simulator_info(self.name)
            self._state = self._status['state']

        except requests.exceptions.Timeout as e:
            log.error('Request timeout in bonsai_ai.Brain: ' + repr(e))
        except Exception as e:
            print(e)
            print('WARNING: ignoring failed update in Brain init.')

    @property
    def ready(self):
        """ Returns True when the BRAIN is ready for training. """
        self.update()
        if self.config.predict:
            return self._state == STOPPED or self._state == COMPLETED
        return self._state == IN_PROGRESS

    @property
    def exists(self):
        self.update()
        """ Returns True when the BRAIN exists (i.e. update succeeded) """
        if self.config.predict:
            return self._state is not None and self._version_exists()

        return self._state is not None

    def sim_exists(self, sim_name):
        self.update()
        if not self._sims:
            return False
        return sim_name in self._sims

    def _version_exists(self):
        for v in self._info['versions']:
            if v['version'] == self.version:
                return True

        return False

    @property
    def state(self):
        """ Returns the current state of the target BRAIN """
        self.update()
        return self._state

    @property
    def status(self):
        """ Returns the current status of the target BRAIN """
        self.update()
        return self._status

    @property
    def sample_rate(self):
        """ Returns the sample rate in iterations/second for
            all simulators connected to the brain """
        self.update()
        try:
            rate = sum(
                sims['sample_rate'] for sims in self._status['simulators'])
            return rate
        except (TypeError, KeyError):
            log.info('Unable to retrieve sample rate from BRAIN ')
            return 0

    @property
    def version(self):
        """ Returns the current BRAIN version number. """
        if self.config.brain_version == 0:
            return self.latest_version
        else:
            return self.config.brain_version

    def training_episode_metrics(self, version=None):
        """
            Returns data about each training episode for a given version of a
            BRAIN. Defaults to configured version if none is given.
            :param version: Version of your brain.
                Defaults to configured version.
        """
        self.update()
        if version is None:
            version = self.version
        return self._api.training_episode_metrics(self.name, version)

    def iteration_metrics(self, version=None):
        """
            Returns iteration data for a given version of a BRAIN.
            Defaults to configured version if none is given. Iterations
            contain data for the number of iterations that have
            occured in a simulation and at what timestamp. This data
            gets logged about once every 100 iterations. This can be useful
            for long episodes when other metrics may not be getting data.
            :param version: Version of your brain.
                Defaults to configured version.
        """
        self.update()
        if version is None:
            version = self.version
        return self._api.iteration_metrics(self.name, version)

    def test_episode_metrics(self, version=None):
        """
            Returns test pass data for a given version of a BRAIN.
            Defaults to configured version if none is given. Test pass
            episodes occur once every 20 training episodes during training
            for a given version of a BRAIN. The value is representative of
            the AI's performance at a regular interval of training
            :param version: Version of your brain.
                Defaults to configured version.
        """
        self.update()
        if version is None:
            version = self.version
        return self._api.test_episode_metrics(self.name, version)
