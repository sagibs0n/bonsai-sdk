"""
Copyright (C) 2019 Microsoft
"""
import json
import os
from uuid import uuid4

from urllib.parse import urljoin
from urllib.request import getproxies

import requests
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

from bonsai_ai.exceptions import BonsaiServerError, UsageError
from bonsai_ai.common.utils import get_user_info
from bonsai_ai.logger import Logger

from typing import Optional

_GET_INFO_URL_PATH_TEMPLATE = "/v1/{username}/{brain}"
_STATUS_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/status"
_SIMS_INFO_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/sims"
_TRAIN_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/train"
_STOP_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/stop"
_RESUME_URL_PATH_TEMPLATE = "/v1/{username}/{brain}/{version}/resume"
_CREATE_BRAIN_URL_PATH_TEMPLATE = "/v1/{username}/brains"
_EDIT_BRAIN_URL_PATH_TEMPLATE = "/v1/{username}/{brain}"
_DELETE_BRAIN_URL_PATH_TEMPLATE = "/v1/{username}/{brain}"
_TEST_METRICS_URL_PATH_TEMPLATE = \
    "/v1/{username}/{brain}/{version}/metrics/test_pass_value"
_TRAIN_METRICS_URL_PATH_TEMPLATE = \
    "/v1/{username}/{brain}/{version}/metrics/episode_value"
_ITERATION_METRICS_URL_PATH_TEMPLATE = \
    "/v1/{username}/{brain}/{version}/metrics/iterations"

log = Logger()


class BrainAPI():
    """
    This object provides an abstraction to use the Brain API. It sets up
    all the necessary parts to make it easy to hit the various endpoints
    that provide information about a Bonsai BRAIN

    In the event of an error the object will raise an error providing the
    consumer details, such as failing response codes and/or error messages.
    """
    def __init__(self, config, timeout=30):
        self._config = config
        self._access_key = config.accesskey
        self._username = config.username
        self._api_url = config.url
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

    def create_brain(self, brain_name, ink_file=None, ink_str=None):
        """
        Creates a brain. A path to an inkling file or a raw inkling string
        can be passed in as arguments to the function. If neither are present,
        a blank BRAIN is created. The inkling file is prioritized over the
        string.

        param brain_name: string
            name of brain
        param inkling_file: string
            path to inkling file
        param inkling_str: string
            raw inkling string
        """
        url_path = _CREATE_BRAIN_URL_PATH_TEMPLATE.format(
            username=self._username
        )
        url = urljoin(self._api_url, url_path)

        if ink_file:
            ink_name, ink_data = self._handle_inkling_file(ink_file)
            json, file_payload = self._generate_payload(
                brain_name, ink_data=ink_data, ink_name=ink_name)
        elif ink_str:
            json, file_payload = self._generate_payload(brain_name, ink_str)
        else:
            json, file_payload = self._generate_payload(brain_name)

        header, body = self._compose_multipart(json, file_payload)
        self._session.headers.update(header)

        return self._http_request('POST', url, body)

    def push_inkling(self, brain_name, ink_file: Optional[str]=None, ink_str=None):
        """
        Pushes inkling to server. A path to an inkling file or a raw inkling
        string can be passed in as arguments to the function. If neither are
        present an error is raised to the caller.

        param brain_name: string
            name of brain
        param inkling_file: string
            path to inkling file
        param inkling_str: string
            raw inkling string
        """
        url_path = _EDIT_BRAIN_URL_PATH_TEMPLATE.format(
            username=self._username,
            brain=brain_name
        )
        url = urljoin(self._api_url, url_path)

        if ink_file:
            ink_name, ink_data = self._handle_inkling_file(ink_file)
            json, file_payload = self._generate_payload(
                brain_name, ink_data=ink_data, ink_name=ink_name)
        elif ink_str:
            json, file_payload = self._generate_payload(brain_name, ink_str)
        else:
            raise UsageError('Push_inkling requires an inkling file or'
                             ' string to be passed in as an argument')

        header, body = self._compose_multipart(json, file_payload)
        self._session.headers.update(header)

        return self._http_request('PUT', url, body)

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

    def _try_http_request(self, http_method, url, data):
        """
        param: http_method -> String: Http method for request, I.E. "GET"
        param: url -> String: url to send request
        param: data -> JSON Formatted Dictionary: json data to send with request
        """

        log.api('Sending {} request to {}'.format(http_method, url))
        request_id = str(uuid4())
        try:
            if http_method == 'GET':
                response = self._session.get(
                    url=url, allow_redirects=False,
                    timeout=self._timeout, headers={'RequestId': request_id})

            elif http_method == 'PUT':
                response = self._session.put(
                    url=url, data=data, headers={'RequestId': request_id},
                    allow_redirects=False, timeout=self._timeout)

            elif http_method == 'POST':
                response = self._session.post(
                    url=url, data=data, allow_redirects=False,
                    timeout=self._timeout, headers={'RequestId': request_id})

            elif http_method == 'DELETE':
                response = self._session.delete(
                    url=url, allow_redirects=False,
                    timeout=self._timeout, headers={'RequestId': request_id})
            else:
                raise UsageError('UNSUPPORTED HTTP METHOD')
        except requests.exceptions.ConnectionError:
            message = \
                "Connection Error, {} Request failed. Unable to connect to " \
                "domain: {}\nRequest ID: {}".format(http_method, url, request_id)
            raise BonsaiServerError(message)
        except requests.exceptions.Timeout:
            message = "{} Request failed. Request to {} timed out" \
                "\nRequest ID: {}".format(http_method, url, request_id)
            raise BonsaiServerError(message)

        try:
            response.raise_for_status()
            self._log_response(response, request_id)
        except requests.exceptions.HTTPError as err:
            self._handle_http_error(response, request_id)
        return self._dict(response)

    def _http_request(self, http_method, url, data=None):
        """
        Wrapper for _try_http_request(), will refresh token and retry if first
        attempt fails due to expired token.

        param: http_method -> String: Http method for request, I.E. "GET"
        param: url -> String: url to send request
        param: data -> JSON Formatted Dictionary: json data to send with request
        """
        try:
            return self._try_http_request(http_method, url, data)
        except BonsaiServerError as err:
            error_lowercase = str(err).lower()
            if 'token' in error_lowercase and 'expired' in error_lowercase:
                self._config.refresh_access_token()
                self._access_key = self._config.accesskey
                self._session.headers.update({
                    'Authorization': self._access_key,
                    'User-Agent': self._user_info
                })
                return self._try_http_request(http_method, url, data)
            else:
                raise err

    @staticmethod
    def _handle_http_error(response, request_id):
        """
        :param response: The response from the server.
        """
        try:
            message = 'Request failed with error message:\n{}'.format(
                response.json()["error"])
        except ValueError:
            message = 'Request failed.'

        message += '\nRequest ID: {}'.format(request_id)

        try:
            message += '\nSpan ID: {}'.format(response.headers['SpanID'])
        except KeyError:
            pass

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
    def _log_response(response, request_id):
        # load json, if any...
        try:
            dump = json.dumps(response.json(), indent=4, sort_keys=True)
        except ValueError:
            dump = "{}"

        log.api("url: {} {}\n\tstatus: {}\n\tjson: {}\n\trequest_id:{}".format(
            response.request.method, response.url,
            response.status_code, dump, request_id))

    @staticmethod
    def _handle_inkling_file(ink_file: str):
        ink_path = os.path.expanduser(ink_file)
        if os.path.exists(ink_path) and os.path.isfile(ink_path):
            relpath = os.path.relpath(ink_path)
            with open(ink_path, 'rb') as f:
                ink_data = f.read()
            return relpath, ink_data
        else:
            raise UsageError()

    @staticmethod
    def _generate_payload(brain_name, ink_data=None, ink_name=None):
        json = {
            "name": brain_name,
            "description": "",
            "project_file": {
                "name": "bonsai_brain.bproj",
                "content": {
                    "files": ['*.ink']
                }
            },
            "project_accompanying_files": []
        }

        if ink_data and ink_name:
            json['project_accompanying_files'] = [ink_name]
            file_payload = {ink_name: ink_data}
        elif ink_data:
            json['project_accompanying_files'] = ['{}.ink'.format(brain_name)]
            file_payload = {'{}.ink'.format(brain_name): ink_data}
        else:
            json["project_file"]["content"]["files"] = []
            file_payload = {}

        return json, file_payload

    @staticmethod
    def _compose_multipart(json_dict, filesdata):
        """ Composes multipart/mixed request for create/edit brain.

        The multipart message is constructed as 1st part application/json and
        subsequent file part(s).

        :param json: dictionary that will be json-encoded
        :param filesdata: dict of <filename> -> <filedata>
        """
        # requests 1.13 does not have high-level support for multipart/mixed.
        # Using lower-level modules to construct multipart/mixed per
        # http://stackoverflow.com/questions/26299889/
        # how-to-post-multipart-list-of-json-xml-files-using-python-requests
        fields = []

        # 1st part: application/json
        rf = RequestField(name="project_data", data=json.dumps(json_dict))
        rf.make_multipart(content_type='application/json')
        fields.append(rf)

        # Subsequent parts: file text
        for filename, filedata in filesdata.items():
            rf = RequestField(name=filename, data=filedata, filename=filename,
                              headers={'Content-Length': len(filedata)})
            rf.make_multipart(content_disposition='attachment',
                              content_type="application/octet-stream")
            fields.append(rf)

        # Compose message
        body, content_type = encode_multipart_formdata(fields)
        # "multipart/form-data; boundary=.." -> "multipart/mixed; boundary=.."
        content_type = content_type.replace("multipart/form-data",
                                            "multipart/mixed",
                                            1)
        headers = {'Content-Type': content_type}

        return (headers, body)
