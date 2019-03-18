# Copyright (C) 2018 Bonsai, Inc.

import json
import functools
import requests
import sys
from .version import __version__

from urllib.parse import urljoin, urlparse, urlunparse

from bonsai_ai.logger import Logger

log = Logger()

# constants for brain state
INKLING_LOADED = 'Inkling Loaded'
NOT_STARTED = 'Not Started'
STARTING = 'Starting'
IN_PROGRESS = 'In Progress'
STOPPED = 'Stopped'
COMPLETED = 'Completed'
FINISHING = 'Finishing'


def _log_response(response):
    # load json, if any...
    try:
        dump = json.dumps(response.json(), indent=4, sort_keys=True)
    except json.JSONDecodeError:
        dump = "{}"

    log.brain("url: {} {}\n\tstatus: {}\n\tjson: {}".format(
              response.request.method, response.url,
              response.status_code, dump))


def _request_info(url, headers, proxy_dict, timeout):
    response = requests.get(
        url=url, headers=headers,
        proxies=proxy_dict, timeout=timeout
    )
    _log_response(response)
    if response.ok:
        """ Example:
        {
            "name": "other",
            "user": "mikest",
            "versions":
                [
                    {
                        "url": "/v1/mikest/other/2",
                        "version": 2
                    },
                    {
                        "url": "/v1/mikest/other/1",
                        "version": 1
                    }
                ],
            "description": ""
        }
        """
        return response.json()
    else:
        response.raise_for_status()


def _request_status(url, headers, proxy_dict, timeout):
    response = requests.get(
        url=url + "/status", headers=headers,
        proxies=proxy_dict, timeout=timeout
    )
    _log_response(response)
    if response.ok:
        """ Example:
        {
            u'episode': 0,
            u'objective_score': 0.0,
            u'models': 1,
            u'episode_length': 0,
            u'iteration': 0,
            u'state': u'Complete',
            u'name': u'other',
            u'simulator_loaded': False,
            u'user': u'mikest',
            u'concepts':
                [
                    {
                        u'concept_name': u'height',
                        u'objective_name': u'???',
                        u'training_end': u'2017-02-23T22:05:02Z',
                        u'training_start': u'2017-02-23T21:05:02Z',
                        u'state': u'Error'
                    }
                ],

            u'objective_name': u'open_ai_gym_default_objective',
            u'training_end': u'2017-02-23T23:05:05.413000Z',
            u'training_start': u'2017-02-23T21:04:58.179000Z'
        }
        """
        return response.json()
    else:
        response.raise_for_status()


def _request_sims(url, headers, proxy_dict, timeout):
    response = requests.get(
        url=url + "/sims", headers=headers,
        proxies=proxy_dict, timeout=timeout
    )
    _log_response(response)
    if response.ok:
        """ Example:
        {
            u'simulator_name': {
                u'inactive': [],
                u'active': []
            }
        }
        """
        return response.json()
    else:
        response.raise_for_status()


def _handle_connection_and_timeout_errors(func):
    """
    Decorator for handling ConnectionErrors and Timeout errors raised 
    by the requests library

    :param func: the function being decorated
    """
    @functools.wraps(func)
    def _handler(self, url, *args, **kwargs):
        try:
            return func(self, url, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            message = \
                "Request failed. Unable to connect to domain: {}".format(url)
            log.error(message)
        except requests.exceptions.Timeout:
            message = "Request failed. Request to {} timed out".format(url)
            log.error(message)

    return _handler


def _handle_http_error(response):
    """
    :param response: The response from the server.
    """
    try:
        message = 'Request failed with error message:\n{}'.format(
            response.json()["error"])
    except:
        message = 'Request failed.'
    log.error(message)


def _dict(response):
    """
    Translates the response from the server into a dictionary. The implication
    is that the server should send back a JSON response for every REST API
    request, and if for some reason, that response is missing, it should be
    treated as an empty JSON message rather than an error. This method will
    change empty responses into empty dictionaries. Responses that are not
    formatted as JSON will log an error.
    :param response: The response from the server.
    :return: Dictionary form the JSON text in the response.
    """
    if response and response.text and response.text.strip():
        try:
            response_dict = response.json()
            return response_dict
        except ValueError as e:
            msg = 'Unable to decode json from {}\n{}'.format(response.url, e)
            log.error(msg)
    return {}


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
        self.config = config
        self._timeout = self.config.network_timeout
        self.description = None
        self.name = name if name else self.config.brain
        self._status = None
        self._info = None
        self._state = None
        self._sims = None
        self.latest_version = None
        self._user_info = self._get_user_info()

        self.update()

    def __repr__(self):
        return '{{'\
            'name: {self.name!r}, ' \
            'description: {self.description!r}, ' \
            'latest_version: {self.latest_version!r}, ' \
            'config: {self.config!r}' \
            '}}'.format(self=self)

    def _brain_url(self):
        """ Utility function to obtain brain url from config.
            Example: http://localhost:5000/v1/nav/brain3 """
        url_base = self.config.url
        url_path = '/v1/{user}/{brain}'.format(
            user=self.config.username,
            brain=self.name
        )
        return urljoin(url_base, url_path)

    @staticmethod
    def _get_user_info():
        """ Get Information about user that will be passed into
            The 'User-Agent' header with requests """
        platform = sys.platform
        python_version = "{}.{}.{}".format(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro)
        user_info = "bonsai-ai/{} (python {}; {})".format(
            __version__, python_version, platform)
        return user_info

    def _train_url(self):
        """ Utility function to obtain training url from config """
        return self._brain_url() + '/train'

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

    def _request_header(self):
        """ Utility function to obtain header that is sent with requests """
        return {'Authorization': self.config.accesskey,
                'User-Agent': self._user_info}

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
            self._info = _request_info(
                self._brain_url(),
                self._request_header(),
                self._proxy_header(),
                self._timeout
                )

            if self._info['versions']:
                self.latest_version = self._info['versions'][0]['version']
            else:
                self.latest_version = 0

            log.brain('Getting {} info...'.format(self.name))
            self._status = _request_status(
                self._brain_url(),
                self._request_header(),
                self._proxy_header(),
                self._timeout
                )

            log.brain('Getting {} sims...'.format(self.name))
            self._sims = _request_sims(
                self._brain_url(),
                self._request_header(),
                self._proxy_header(),
                self._timeout
            )
            self._state = self._status['state']

        except requests.exceptions.Timeout as e:
            log.error('Request timeout in bonsai_ai.Brain: ' + repr(e))
        except Exception as e:
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
        if version is None:
            version = self.version
        self.update()
        url = '{}/{}/metrics/episode_value'.format(
            self._brain_url(), version
        )
        log.brain('Getting training episode metrics from {}'.format(url))
        response = self._get(url)
        return response

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
        if version is None: 
            version = self.version
        self.update()
        url = '{}/{}/metrics/iterations'.format(
            self._brain_url(), version
        )
        log.brain('Getting iteration metrics from {}'.format(url))
        response = self._get(url)
        return response

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
        if version is None:
            version = self.version
        self.update()
        url = '{}/{}/metrics/test_pass_value'.format(
            self._brain_url(), version
        )
        log.brain('Getting test episode metrics from {}'.format(url))
        response = self._get(url)
        return response

    @_handle_connection_and_timeout_errors
    def _get(self, url):
        response = requests.get(
            url=url,
            headers=self._request_header(),
            proxies=self._proxy_header(),
            allow_redirects=False,
            timeout=self._timeout
        )
        try:
            response.raise_for_status()
            _log_response(response)
        except requests.exceptions.HTTPError:
            _handle_http_error(response)
        return _dict(response)
