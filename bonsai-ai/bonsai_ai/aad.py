# pyright: strict
import os
import atexit
import requests
from uuid import uuid4
from urllib.parse import urljoin
from bonsai_ai.logger import Logger
from bonsai_ai.token_cache import BonsaiTokenCache
from bonsai_ai.exceptions import AuthenticationError
from bonsai_ai.common.utils import get_user_info
from msal import PublicClientApplication
from requests.exceptions import (ConnectionError, Timeout)

# turns on msal debugging
# import logging
# logging.basicConfig(level=logging.DEBUG)

log = Logger()

_AAD_CLIENT_ID = '23e69e0c-5143-40dd-90ca-a6a8cc478db5'
_AAD_AUTHORITY = 'https://login.microsoftonline.com/organizations'
_AAD_SCOPE = ['api://23e69e0c-5143-40dd-90ca-a6a8cc478db5/Bonsai.Read']
_USERPROPERTIES_URI = '/v1/userproperties'


def write_cache_to_file(cache: BonsaiTokenCache):
    cache.write_cache_to_file()


class AADRequestHelper():

    def __init__(self, base_url: str, auth_token: str):
        if not base_url:
            raise AuthenticationError('No url set, cannot retrieve workspace')
        self._base_url = base_url
        self._auth_token = auth_token
        self._session = self._get_session()

    def _get_session(self):
        session = requests.Session()
        headers = self._get_headers()
        session.headers.update(headers)
        return session

    def _get_headers(self):
        return {
            'Authorization': self._auth_token,
            'User-Agent': get_user_info()
        }

    def perform_get(self, url: str):
        request_id = str(uuid4())
        try:
            response = self._session.get(url=url,
                                         allow_redirects=False,
                                         timeout=30,
                                         headers={'RequestId': request_id})
        except ConnectionError:
            message = "GET request failed. Unable to connect to " \
                "domain: {}\nRequest ID: {}".format(url, request_id)
            raise AuthenticationError(message)
        except Timeout:
            message = "GET Request failed. Request to {} timed out" \
                "\nRequest ID: {}".format(url, request_id)
            raise AuthenticationError(message)
        return response

    def get_workspace(self) -> str:
        url = urljoin(self._base_url, _USERPROPERTIES_URI)
        response = self.perform_get(url)
        try:
            response_dict = response.json()
            return response_dict['properties']['workspace']
        except KeyError as e:
            message = 'Could not extract workspace from server response. ' \
                      'Response: {}\nException: {}'.format(response.text, e)
            raise AuthenticationError(message)


class AADClient(object):
    """
    This object uses the Microsoft Authentication Library for Python (MSAL)
    to log in and authenticate users using AAD.

    The only public method is get_access_token(), which returns an access token
    if one already exists in the cache, else it will fill the cache by
    prompting the user to log in.
    """

    def __init__(self, url: str):
        self._base_url = url
        self.cache = BonsaiTokenCache()
        atexit.register(write_cache_to_file, self.cache)

        retry_count = 1
        while True:
            try:
                self._app = PublicClientApplication(_AAD_CLIENT_ID,
                                                    authority=_AAD_AUTHORITY,
                                                    token_cache=self.cache)
                if self._app:
                    break
            except ConnectionError as e:
                log.info('ConnectionError on attempt {} to '
                         'create msal PublicClientApplication, '
                         'retrying...'.format(retry_count))
                if retry_count >= 5:
                    raise e
            retry_count += 1

    def _log_in_with_device_code(self) -> dict:
        """ Recommended login method. The user must open a browser to
            https://microsoft.com/devicelogin and enter a unique device code to
            begin authentication. """
        flow = self._app.initiate_device_flow(_AAD_SCOPE)
        print(flow["message"])
        return self._app.acquire_token_by_device_flow(flow)

    def _log_in_with_password(self) -> dict:
        """ This login method is less secure and should be used for
            automation only. """
        return self._app.acquire_token_by_username_password(
            os.environ['BONSAI_AAD_USER'],
            os.environ['BONSAI_AAD_PASSWORD'],
            _AAD_SCOPE)

    def _get_access_token_from_cache(self):
        """ This also does a token refresh if the access token has expired. """
        result = None
        accounts = self._app.get_accounts()
        if accounts:
            """ Bonsai config only gives us the short username, and token cache
            stores accounts by email address (e.g. soc-auto vs
            soc-auto@microsoft.com). So, if there are multiple accounts, assume
            the first one for now. """
            chosen = accounts[0]
            result = self._app.acquire_token_silent(_AAD_SCOPE, account=chosen)
        return result

    def get_access_token(self):

        # attempt to get token from cache
        token = self._get_access_token_from_cache()
        if token:
            return 'Bearer {}'.format(token['access_token'])

        # no token found in cache, user must sign in and try again
        if ('BONSAI_AAD_USER' in os.environ and
                'BONSAI_AAD_PASSWORD' in os.environ):
            self._log_in_with_password()
        else:
            print('No access token found in cache, please sign in.')
            self._log_in_with_device_code()
        token = self._get_access_token_from_cache()
        if token:
            return "Bearer {}".format(token['access_token'])

        message = 'Error: could not fetch AAD access token after login.'
        raise AuthenticationError(message)

    def get_workspace(self):

        # attempt to get workspace from cache
        workspace = self.cache.get_workspace()
        if workspace:
            return workspace

        # make sure we have access token to request workspace
        auth_token = self.get_access_token()

        # get workspace, store to cache and return
        helper = AADRequestHelper(self._base_url, auth_token)
        self.workspace = helper.get_workspace()
        self.cache.set_workspace(self.workspace)
        return self.workspace
