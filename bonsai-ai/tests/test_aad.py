# Copyright (C) 2019 Microsoft, Inc.

import os
import pytest
from bonsai_ai.exceptions import AuthenticationError
from bonsai_ai.aad import (AADRequestHelper, AADClient)


_DUMMY_API_URL = 'https://test-api.azdev.bons.ai'
_DUMMY_AUTH_TOKEN = 'token'


def test_initialize_helper():
    helper = AADRequestHelper(_DUMMY_API_URL, _DUMMY_AUTH_TOKEN)
    headers = helper._get_headers()
    assert 'User-Agent' in headers
    assert headers['Authorization'] == _DUMMY_AUTH_TOKEN


def test_helper_get_workspace(aad_workspace, aad_get_accounts):
    helper = AADRequestHelper(_DUMMY_API_URL, _DUMMY_AUTH_TOKEN)
    workspace = helper.get_workspace()
    assert workspace == '123456789'


def test_helper_not_allow_listed(aad_workspace_not_allow_listed,
                                 aad_get_accounts):
    helper = AADRequestHelper(_DUMMY_API_URL, _DUMMY_AUTH_TOKEN)
    with pytest.raises(AuthenticationError) as e:
        workspace = helper.get_workspace()


def test_client_from_cache(aad_workspace, aad_get_accounts, aad_token_cache):
    client = AADClient(_DUMMY_API_URL)
    assert client.get_access_token() == 'Bearer abcdefghijklmnopqrstuvwxyz'
    assert client.get_workspace() == '123456789'


def test_empty_client_username_password(aad_workspace,
                                        aad_get_accounts_fail_first,
                                        aad_token_cache,
                                        aad_username_password):
    os.environ['BONSAI_AAD_USER'] = 'username'
    os.environ['BONSAI_AAD_PASSWORD'] = 'password'
    client = AADClient(_DUMMY_API_URL)
    assert client.get_access_token() == 'Bearer abcdefghijklmnopqrstuvwxyz'
    assert client.get_workspace() == '123456789'
    del os.environ['BONSAI_AAD_USER']
    del os.environ['BONSAI_AAD_PASSWORD']


def test_empty_client_device_code(aad_workspace,
                                  aad_get_accounts_fail_first,
                                  aad_token_cache,
                                  aad_device_code):
    client = AADClient(_DUMMY_API_URL)
    assert client.get_access_token() == 'Bearer abcdefghijklmnopqrstuvwxyz'
    assert client.get_workspace() == '123456789'
