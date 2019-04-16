"""
Copyright (C) 2019 Microsoft
"""
import functools
import json

from urllib.parse import urljoin
from urllib.request import getproxies

import requests

from bonsai_ai.exceptions import BonsaiServerError, UsageError
from bonsai_ai.common.utils import get_user_info
from bonsai_ai.logger import Logger

_GET_INFO_URL_PATH_TEMPLATE = "/v1/{username}/{brain}"
_STATUS_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/status"
_SIMS_INFO_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/sims"
_TRAIN_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/train"
_STOP_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/stop"
_RESUME_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/{version}/resume"
_DELETE_BRAIN_URL_PATH_TEMPLATE = "/v1/{username}/{brain}"
_TEST_METRICS_URL_PATH_TEMPLATE = \
    "/v1/{username}/{brain}/{version}/metrics/test_pass_value"
_TRAIN_METRICS_URL_PATH_TEMPLATE = \
    "/v1/{username}/{brain}/{version}/metrics/episode_value"
_ITERATION_METRICS_URL_PATH_TEMPLATE = \
    "/v1/{username}/{brain}/{version}/metrics/iterations"

log = Logger()


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
            raise BonsaiServerError(message)
        except requests.exceptions.Timeout:
            message = "Request failed. Request to {} timed out".format(url)
            raise BonsaiServerError(message)
    return _handler


class BrainAPI():
    """
    This object provides an abstraction to use the Brain API. It sets up
    all the necessary parts to make it easy to hit the various endpoints
    that provide information about a Bonsai BRAIN

    In the event of an error the object will raise an error providing the
    consumer details, such as failing response codes and/or error messages.
    """
    def __init__(self, access_key, username, api_url, timeout=30):
        self._access_key = access_key
        self._username = username
        self._api_url = api_url
        self._timeout = timeout
        self._user_info = get_user_info()
        self._session = requests.Session()
        self._session.proxies = getproxies()
        self._session.headers.update({
            'Authorization': self._access_key,
            'User-Agent': self._user_info
        })
        self._http_methods = {'GET', 'PUT', 'POST', 'DELETE'}

    def get_brain_info(self, brain_name):
        url_path = _GET_INFO_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('GET', url)

    def get_brain_status(self, brain_name):
        url_path = _STATUS_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('GET', url)

    def get_simulator_info(self, brain_name):
        url_path = _SIMS_INFO_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('GET', url)

    def start_training(self, brain_name):
        url_path = _TRAIN_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('PUT', url)

    def stop_training(self, brain_name):
        url_path = _STOP_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('PUT', url)

    def resume_training(self, brain_name, version='latest'):
        url_path = _RESUME_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name,
            version=version
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('PUT', url)

    def training_episode_metrics(self, brain_name, version):
        url_path = _TRAIN_METRICS_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name,
            version=version
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('GET', url)

    def test_episode_metrics(self, brain_name, version):
        url_path = _TEST_METRICS_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name,
            version=version
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('GET', url)

    def iteration_metrics(self, brain_name, version):
        url_path = _ITERATION_METRICS_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name,
            version=version
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('GET', url)

    def delete_brain(self, brain_name):
        url_path = _DELETE_BRAIN_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name,
        )
        url = urljoin(self._api_url, url_path)
        return self._http_request('DELETE', url)

    @_handle_connection_and_timeout_errors
    def _http_request(self, http_method, url, data=None):
        """
        param: http_method -> String: Http method for request, I.E. "GET"
        param: url -> String: url to send request
        param: data -> JSON Formatted Dictionary: json data to send with request
        """

        if http_method not in self._http_methods:
            raise UsageError(
                'Pass in one of the following accepted http_methods\n' \
                '{}'.format(self._http_methods))

        log.api('Sending {} request to {}'.format(http_method, url))

        if http_method == 'GET':
            response = self._session.get(
                url=url, allow_redirects=False, timeout=self._timeout)

        elif http_method == 'PUT':
            response = self._session.put(
                url=url, json=data,
                allow_redirects=False, timeout=self._timeout)

        elif http_method == 'POST':
            raise UsageError('NOT IMPLEMENTED YET')

        elif http_method == 'DELETE':
            response = self._session.delete(
                url=url, allow_redirects=False, timeout=self._timeout)

        else:
            raise UsageError('UNSUPPORTED HTTP METHOD')

        try:
            response.raise_for_status()
            self._log_response(response)
        except requests.exceptions.HTTPError:
            self._handle_http_error(response)
        return self._dict(response)

    @staticmethod
    def _handle_http_error(response):
        """
        :param response: The response from the server.
        """
        try:
            message = 'Request failed with error message:\n{}'.format(
                response.json()["error"])
        except ValueError:
            message = 'Request failed.'
        raise BonsaiServerError(message)

    @staticmethod
    def _dict(response):
        """
        Translates the response from the server into a dictionary. The
        implication is that the server should send back a JSON response
        for every REST API request, and if for some reason, that response
        is missing, it should be treated as an empty JSON message rather
        than an error. This method will change empty responses into empty
        dictionaries. Responses that are not formatted as JSON will log an
        error.
        :param response: The response from the server.
        :return: Dictionary form the JSON text in the response.
        """
        if response and response.text and response.text.strip():
            try:
                response_dict = response.json()
                return response_dict
            except ValueError as e:
                msg = 'Unable to decode json from {}\n{}'.format(
                    response.url, e)
                log.error(msg)
        return {}

    @staticmethod
    def _log_response(response):
        # load json, if any...
        try:
            dump = json.dumps(response.json(), indent=4, sort_keys=True)
        except ValueError:
            dump = "{}"

        log.api("url: {} {}\n\tstatus: {}\n\tjson: {}".format(
            response.request.method, response.url, response.status_code, dump))
