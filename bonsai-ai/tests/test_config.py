# pylint: disable=missing-docstring
import os
import pytest
import sys
from configparser import NoSectionError
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


def test_config_with_argv_and_dev_profile(temp_dot_bonsai):
    config = Config(argv=sys.argv, profile='dev')
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'
    assert config.username == 'admin'
    assert config.url.startswith('http://localhost')


def test_config_with_different_profile(temp_dot_bonsai):
    config = Config(profile='dev')
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'


@pytest.mark.xfail(raises=NoSectionError)
def test_config_with_missing_profile():
    config = Config(profile='doesnt_exist')


def test_config_assignments(temp_dot_bonsai):
    config = Config(profile='dev')
    assert config.url == 'http://localhost'
    assert config.username == 'admin'
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'


def test_config_default_url(temp_dot_bonsai):
    config = Config()
    config._update(profile='test_default_url')
    config.url == 'https://api.bons.ai'


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


def test_verbose_logging(capsys, temp_dot_bonsai):
    config = Config([
        __name__,
        '--verbose'
        ])
    log = Logger()
    assert(config.verbose is True)
    assert(log._enable_all is True)


def test_config_has_section(temp_dot_bonsai):
    config = Config()
    assert config._has_section('dev') is True


def test_config_doesnt_have_section(temp_dot_bonsai):
    config = Config()
    assert config._has_section('doesnt_exist') is False


def test_default_retry_timeout():
    config = Config()
    assert config.retry_timeout == 300


def test_argv_retry_timeout():
    config = Config([
        __name__,
        '--retry-timeout', '10'
    ])
    assert config.retry_timeout == 10


@pytest.mark.xfail(raises=ValueError, strict=True)
def test_invalid_retry_timeout_throws_error():
    config = Config([
        __name__,
        '--retry-timeout', '-1000'
    ])


def test_default_pong_interval():
    config = Config()
    assert config.pong_interval == 15


def test_argv_pong_interval():
    config = Config([
        __name__,
        '--pong-interval', '10'
    ])
    assert config.pong_interval == 10


def test_valid_pong_intervals():
    config = Config()
    config.pong_interval = 1
    config.pong_interval = 0
    config.pong_interval = 239


def test_invalid_pong_interval_throws_error():
    config = Config()
    with pytest.raises(ValueError):
        config.pong_interval = -1
    with pytest.raises(ValueError):
        config.pong_interval = 0.1
    with pytest.raises(ValueError):
        config.pong_interval = 250


@pytest.mark.xfail(raises=SystemExit, strict=True)
def test_invalid_retry_timeout_argv_throws_error():
    """ Incorrect values in argparse raise a SystemExit """
    config = Config([
        __name__,
        '--pong-interval', 'foo'
    ])


def test_argv_accesskey():
    config = Config([
        __name__,
        '--access-key', '01001'
    ])
    assert config.accesskey == '01001'

    config = Config([
        __name__,
        '--accesskey', '22222'
    ])
    assert config.accesskey == '22222'

if __name__ == '__main__':
    pytest.main([__file__])
