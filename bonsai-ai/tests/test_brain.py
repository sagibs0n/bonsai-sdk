# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
import pytest
import os

try:
    from unittest.mock import Mock, patch, ANY
except ImportError:
    from mock import Mock, patch, ANY

from bonsai_ai import Brain, Config
from bonsai_ai.brain import IN_PROGRESS, STOPPED


def test_brain(train_config):
    """ Tests that a brain is created without errors """
    # Patch and Mock out requests/responses
    brain = Brain(train_config, 'SOMENAME')

    assert brain.config == train_config
    assert brain.name == 'SOMENAME'
    assert brain.description is None
    assert brain.latest_version == 1


def test_brain_update(blank_brain, v2_get):
    """ Tests brain update function """
    assert blank_brain.exists()
    assert blank_brain.state == IN_PROGRESS
    assert blank_brain.ready()
    assert blank_brain.latest_version == 1
    blank_brain.update()
    assert not blank_brain.ready()
    assert blank_brain.state == STOPPED
    assert blank_brain.exists()
    assert blank_brain.latest_version == 2


def test_brain_predict_version():
    """ Tests brain version property """
    config = Config([__name__, '--predict=4'])
    brain = Brain(config)
    assert brain.config.predict is True
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


def test_brain_no_proxy():
    config = Config([__name__])
    brain = Brain(config)
    assert brain._proxy_header() is None


def test_brain_with_proxy():
    # Patch and Mock out requests/responses
    set_proxies(http_proxy='pass',
                https_proxy=None,
                all_proxy=None)
    config = Config([__name__])
    brain = Brain(config)
    assert brain._proxy_header() is not None


def test_brain_name_is_not_none(train_config):
    brain = Brain(train_config)
    assert brain.name is not None


if __name__ == '__main__':
    pytest.main([__file__])
