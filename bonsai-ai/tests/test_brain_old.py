# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
import pytest
import os
import requests

try:
    from unittest.mock import Mock, patch, ANY
except ImportError:
    from mock import Mock, patch, ANY

from bonsai_ai import Brain, Config


@patch('requests.get')
def test_brain(mock_get):
    """ Tests that a brain is created without errors """
    # Patch and Mock out requests/responses
    response = Mock()
    test_json = {'versions': [{'version': 1}],
                 'state': 'DONE'}
    response.json.return_value = test_json
    mock_get.return_value = response

    # create config object
    config = Config([
        __name__,
        '--accesskey=VALUE',
        '--username=VALUE',
        '--url=VALUE',
        '--brain=VALUE',
        '--proxy=VALUE'
        ])
    brain = Brain(config, 'SOMENAME')

    assert brain.config == config
    assert brain.name == 'SOMENAME'
    assert brain.description is None
    assert brain.latest_version == 1


@pytest.mark.xfail(raises=(TypeError))
def test_brain_create_with_invalid_args():
    brain = Brain()


@pytest.mark.xfail(raises=(requests.HTTPError))
def test_brain_create_with_invalid_brain():
    config = Config([__name__, '--brain=INVALIDBRAIN'])
    brain = Brain(config)


@patch('requests.get')
def test_brain_update(mock_get):
    """ Tests brain update function """
    # Patch and Mock out requests/responses
    response = Mock()
    test_json = {'versions': [{'version': 1}],
                 'state': 'DONE'}
    response.json.return_value = test_json
    mock_get.return_value = response

    config = Config([__name__])
    brain = Brain(config)

    assert mock_get.call_count == 2
    brain.update()
    assert mock_get.call_count == 4


@patch('requests.get')
def test_brain_ready(mock_get):
    """ Tests brain ready function """
    # Patch and Mock out requests/responses
    response = Mock()
    test_json = {'versions': [{'version': 1}],
                 'state': 'In Progress'}
    response.json.return_value = test_json
    mock_get.return_value = response

    config = Config([__name__])
    brain = Brain(config)

    assert brain.ready() is True


@patch('requests.get')
def test_brain_version(mock_get):
    """ Tests brain version property """
    # Patch and Mock out requests/responses
    response = Mock()
    test_json = {'versions': [{'version': 1}],
                 'state': 'In Progress'}
    response.json.return_value = test_json
    mock_get.return_value = response

    config = Config([__name__, '--predict=4'])
    brain = Brain(config)
    assert brain.config.brain_version == 4
    assert brain.version == 4


def set_proxies(http_proxy, https_proxy, all_proxy):
    def update_env_key(key, value=None):
        if value is None:
            try:
                del os.environ[key]
            except:
                pass
        else:
            os.environ[key] = value

    update_env_key('http_proxy', http_proxy)
    update_env_key('https_proxy', https_proxy)
    update_env_key('all_proxy', all_proxy)


@patch('requests.get')
def test_requests_called_with_no_proxy(mock_get):
    # Patch and Mock out requests/responses
    response = Mock()
    test_json = {'versions': [{'version': 1}],
                 'state': 'In Progress'}
    response.json.return_value = test_json
    mock_get.return_value = response

    config = Config([__name__, '--predict=4'])
    brain = Brain(config)

    proxies = brain._proxy_header()
    mock_get.assert_called_with(headers=ANY, proxies=proxies, url=ANY)


@patch('requests.get')
def test_requests_called_with_http_proxy(mock_get):
    # Patch and Mock out requests/responses
    response = Mock()
    test_json = {'versions': [{'version': 1}],
                 'state': 'In Progress'}
    response.json.return_value = test_json
    mock_get.return_value = response

    set_proxies(http_proxy='pass',
                https_proxy=None,
                all_proxy=None)
    config = Config([__name__, '--predict=4'])
    brain = Brain(config)

    proxies = brain._proxy_header()
    mock_get.assert_called_with(headers=ANY, proxies=proxies, url=ANY)


if __name__ == '__main__':
    pytest.main([__file__])
