# Copyright (C) 2019 Microsoft
"""
Brain Controller
"""
import functools
from bonsai_ai.brain_api import BrainAPI
from bonsai_ai.logger import Logger
from bonsai_ai.exceptions import BonsaiServerError

log = Logger()

def _handle_server_errors(func):
    @functools.wraps(func)
    def _handler(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except BonsaiServerError as err:
            log.error(err)
    return _handler

class BrainController():
    """
    Brain Controller
    """
    def __init__(self, config):
        self._config = config
        self._api = BrainAPI(config=config, timeout=config.network_timeout)

    @_handle_server_errors
    def create(self, name, ink_file=None, ink_str=None):
        """
        Creates a BRAIN. A path to an inkling file or a raw inkling string
        can be passed in as arguments to the function. If neither are present,
        a blank BRAIN is created. The inkling file is prioritized over the
        string.

        param name: string
            name of brain
        param inkling_file: string
            path to inkling file
        param inkling_str: string
            raw inkling string
        """
        response = self._api.create_brain(name, ink_file, ink_str)
        return response

    @_handle_server_errors
    def delete(self, name):
        """
        Deletes a BRAIN.

        param name: string
            name of brain
        """
        response = self._api.delete_brain(name)
        return response

    @_handle_server_errors
    def push_inkling(self, name, ink_file=None, ink_str=None):
        """
        Pushes inkling to server. A path to an inkling file or a raw inkling
        string can be passed in as arguments to the function. If neither are
        present an error is raised to the caller.

        param name: string
            name of brain
        param inkling_file: string
            path to inkling file
        param inkling_str: string
            raw inkling string
        """
        response = self._api.push_inkling(name, ink_file, ink_str)
        return response

    @_handle_server_errors
    def train_start(self, name):
        """
        Starts training for a BRAIN

        param name: string
            name of brain
        """
        response = self._api.start_training(name)
        return response

    @_handle_server_errors
    def train_stop(self, name):
        """
        Stops training for a BRAIN

        param name: string
            name of brain
        """
        response = self._api.stop_training(name)
        return response

    @_handle_server_errors
    def train_resume(self, name, version='latest'):
        """
        Starts training for a BRAIN

        param name: string
            name of brain
        param version: string
            Version of BRAIN. Defaults to 'latest'
        """
        response = self._api.resume_training(name, version)
        return response

    @_handle_server_errors
    def status(self, name):
        """
        Retrieves status for a BRAIN

        param name: string
            name of brain
        """
        response = self._api.get_brain_status(name)
        return response

    @_handle_server_errors
    def info(self, name):
        """
        Retrieves BRAIN information.

        param name: string
            name of brain
        """
        response = self._api.get_brain_info(name)
        return response

    @_handle_server_errors
    def sample_rate(self, name):
        """
        Retrieves sample rate for a given BRAIN.

        param name: string
            name of brain
        """
        try:
            response = self._api.get_brain_status(name)
            rate = sum(sims['sample_rate'] for sims in response['simulators'])
            return rate
        except(TypeError, KeyError) as err:
            log.error(err)
            log.error('Unable to determine sample rate from response')
            return 0

    @_handle_server_errors
    def simulator_info(self, name):
        """
        Retrieves simulator information for a given BRAIN.

        param name: string
            name of brain
        """
        response = self._api.get_simulator_info(name)
        return response

    @_handle_server_errors
    def training_episode_metrics(self, name, version='latest'):
        """
        Retrieves training episode metrics for a given BRAIN.

        param name: string
            name of brain
        param version: string
            verion of BRAIN. defaults to 'latest'
        """
        response = self._api.training_episode_metrics(name, version)
        return response

    @_handle_server_errors
    def test_episode_metrics(self, name, version='latest'):
        """
        Retrieves test episode metrics for a given BRAIN.

        param name: string
            name of brain
        param version: string
            verion of BRAIN. defaults to 'latest'
        """
        response = self._api.test_episode_metrics(name, version)
        return response

    @_handle_server_errors
    def iteration_metrics(self, name, version='latest'):
        """
        Retrieves iteration metrics for a given BRAIN.

        param name: string
            name of brain
        param version: string
            verion of BRAIN. defaults to 'latest'
        """
        response = self._api.iteration_metrics(name, version)
        return response
