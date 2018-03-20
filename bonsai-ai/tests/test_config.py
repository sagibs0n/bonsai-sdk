# pylint: disable=missing-docstring
import os
import pytest
import sys
from bonsai_ai import Config
from bonsai_ai.logger import Logger


@pytest.mark.parametrize(
    "predict_flag, expected_version",
    [('--predict=1', 1),
     ('--predict=latest', 0),
     ('--predict', 0)])
def test_valid_predict_version(predict_flag, expected_version):
    config = Config([__name__, predict_flag])
    assert config.brain_version is expected_version


def test_missing_predict_flag():
    config = Config([__name__])
    assert config.predict is False


@pytest.mark.xfail(raises=(RuntimeError, ValueError), strict=True)
@pytest.mark.parametrize(
    "invalid_value",
    ['--predict=blah',
     '--predict=@',
     '--predict=_',
     '--predict=',
     '--predict=-1'])
def test_invalid_predict_version(invalid_value):
    # to verify error log, catch and inspect instead of expecting fail (xfail)
    config = Config([__name__, invalid_value])
    assert False, \
        "Expected {} to throw an error".format(invalid_value)


def test_basic_argument_settings():
    config = Config([
        __name__,
        '--accesskey=VALUE',
        '--username=VALUE',
        '--url=VALUE',
        '--brain=VALUE',
        '--proxy=VALUE',
        ])
    assert config.accesskey == 'VALUE'
    assert config.username == 'VALUE'
    assert config.url == 'VALUE'
    assert config.proxy == 'VALUE'
    assert config.brain == 'VALUE'
    # NOTE: no way to test these at the moment as config doesn't expose
    # logging interface.
    # log parameters
    # config = Config([
    #     __name__,
    #     '--log=foo',
    #     'bar',
    #     'baz',
    #     ])
    # assert config.log is ['foo', 'bar', 'baz']

    # config = Config([__name__, '--verbose=true'])
    # assert config.log contains 'all'

    # config = Config([__name__, '--log=none'])
    # assert config.log is empty


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


def test_no_proxy():
    set_proxies(http_proxy=None,
                https_proxy=None,
                all_proxy=None)
    config = Config()
    assert config.proxy is None


def test_just_http_proxy():
    set_proxies(http_proxy='pass',
                https_proxy=None,
                all_proxy='fail')
    config = Config()
    assert config.proxy == 'pass'


def test_http_proxy_fallback_for_https_url():
    set_proxies(http_proxy='pass',
                https_proxy=None,
                all_proxy=None)
    config = Config()
    config.url = 'https://localhost'
    assert config.proxy == 'pass'


def test_https_preferred_over_http():
    set_proxies(http_proxy='pass',
                https_proxy='https',
                all_proxy=None)
    config = Config()
    config.url = 'https://localhost'
    assert config.proxy == 'https'
    config.url = 'http://localhost'
    assert config.proxy == 'pass'


def test_http_is_fallback_for_https():
    set_proxies(http_proxy=None,
                https_proxy='pass',
                all_proxy='all')
    config = Config()
    config.url = 'https://localhost'
    assert config.proxy == 'pass'
    config.url = 'http://localhost'
    assert config.proxy == 'all'


@pytest.mark.xfail(raises=(RuntimeError, ValueError), strict=True)
def test_assignment_of_poorly_formatted_proxy():
    config = Config()
    config.proxy = "http://foo:bar"


def test_commandline_overrides_other_settings():
    config = Config([__name__, '--proxy=PASS'])
    config.url = 'http://localhost'
    assert config.proxy == 'PASS'


def test_config_with_argv():
    config = Config(sys.argv)
    assert True


def test_config_with_argv_and_dev_profile():
    config = Config(sys.argv, 'dev')
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'
    assert config.username == 'admin'
    assert config.url.startswith('http://localhost:')


def test_config_with_different_profile():
    config = Config(profile='dev')
    print("config url: {}".format(config.url))
    print("config username: {}".format(config.username))
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'


def test_config_with_missing_profile():
    config = Config(profile='doesnt_exist')
    assert config.url is None, "default url should be empty"
    assert config.accesskey == 'None', "default accesskey should be None"
    assert config.username == 'admin', "default usernamer should be None"


def test_config_assignments():
    config = Config()
    config.url = 'http://somewhere'
    assert config.url == 'http://somewhere'

    config.accesskey = '123'
    assert config.accesskey == '123'

    config.username = 'bob'
    assert config.username == 'bob'

    config.predict = True
    assert config.predict is True

    config.predict_version = 3
    assert config.predict_version == 3


def test_logging_config():
    config = Config([
        __name__,
        '--log', 'v1', 'v2', 'v3'
        ])
    log = Logger()
    assert(config.verbose is False)
    assert('v1' in log._enabled_keys)
    assert('v2' in log._enabled_keys)
    assert('v3' in log._enabled_keys)
    assert('v4' not in log._enabled_keys)
    log._enabled_keys = {}


def test_verbose_logging():
    config = Config([
        __name__,
        '--verbose'
        ])
    log = Logger()
    assert(config.verbose is True)
    assert(log._enable_all is True)
    assert(len(log._enabled_keys.keys()) == 0)


def test_config_has_section():
    config = Config()
    assert config._has_section('dev') is True


def test_config_doesnt_have_section():
    config = Config()
    assert config._has_section('doesnt_exist') is False


def test_config_update():
    config = Config()
    config._update(url='http://somewhere', accesskey='123', username='bob')
    assert config.url == 'http://somewhere'
    assert config.accesskey == '123'
    assert config.username == 'bob'

if __name__ == '__main__':
    pytest.main([__file__])
