# pylint: disable=missing-docstring
import os
import pytest
import sys
import json
import atexit

from bonsai_ai import Config
from bonsai_ai.aad import write_cache_to_file, AADClient
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


@pytest.mark.parametrize(
    "invalid_value",
    ['--predict=blah',
     '--predict=@',
     '--predict=_',
     '--predict=',
     '--predict=-1'])
def test_invalid_predict_version(invalid_value):
    # to verify error log, catch and inspect instead of expecting fail (xfail)
    try:
        config = Config([__name__, invalid_value])
    except (RuntimeError, ValueError) as e:
        return

    assert False, "XFAIL"


def test_basic_argument_settings():
    config = Config([
        __name__,
        '--accesskey=VALUE',
        '--username=VALUE',
        '--url=VALUE',
        '--brain=VALUE',
        ])
    assert config.accesskey == 'VALUE'
    assert config.username == 'VALUE'
    assert config.url == 'VALUE'
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


def unset_proxies():
    vars = ['http_proxy', 'https_proxy', 'all_proxy']
    for v in vars:
        if v in os.environ:
            del os.environ[v]


def test_no_proxy():
    set_proxies(http_proxy=None,
                https_proxy=None,
                all_proxy=None)
    config = Config()
    assert config.proxy is None
    unset_proxies()


def test_just_http_proxy():
    set_proxies(http_proxy='pass',
                https_proxy=None,
                all_proxy='fail')
    config = Config()
    assert config.proxy == 'pass'
    unset_proxies()


def test_http_proxy_fallback_for_https_url():
    set_proxies(http_proxy='pass',
                https_proxy=None,
                all_proxy=None)
    config = Config()
    config.url = 'https://localhost'
    assert config.proxy == 'pass'
    unset_proxies()


def test_https_preferred_over_http():
    set_proxies(http_proxy='pass',
                https_proxy='https',
                all_proxy=None)
    config = Config()
    config.url = 'https://localhost'
    assert config.proxy == 'https'
    config.url = 'http://localhost'
    assert config.proxy == 'pass'
    unset_proxies()


def test_http_is_fallback_for_https():
    set_proxies(http_proxy=None,
                https_proxy='pass',
                all_proxy='all')
    config = Config()
    config.url = 'https://localhost'
    assert config.proxy == 'pass'
    config.url = 'http://localhost'
    assert config.proxy == 'all'
    unset_proxies()


def test_assignment_of_poorly_formatted_proxy():
    try:
        config = Config()
        config.proxy = "http://foo:bar"
    except (RuntimeError, ValueError) as e:
        return

    assert False, "XFAIL"


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
    assert config.url.startswith('http://127.0.0.1')


def test_config_with_different_profile(temp_dot_bonsai):
    config = Config(profile='dev')
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'


def test_config_with_missing_profile():
    # should not fail on missing profile
    config = Config(profile='doesnt_exist')


def test_config_assignments(temp_dot_bonsai):
    config = Config(profile='dev')
    assert config.url == 'http://127.0.0.1'
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


def test_invalid_retry_timeout_throws_error():
    try:
        config = Config([
            __name__,
            '--retry-timeout', '-1000'
        ])
    except ValueError as e:
        return

    assert False, "XFAIL"


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


def test_config_repr_is_json(temp_dot_bonsai):
    config = Config()
    json.loads(str(config))


def test_config_update_creates_profile(temp_dot_bonsai):
    """ Tests that the update function creates a profile if it does
        not exist instead of throwing a NoSectionError """
    config = Config(profile='FOO')
    config._update(url='BAR')
    assert config._has_section('FOO') is True


def test_config_works_if_permission_error(temp_home_directory_read_only):
    config = Config()


def test_aad_control_plane(temp_dot_bonsai,
                           aad_workspace,
                           aad_get_accounts,
                           aad_token_cache):
    config = Config(argv=sys.argv, profile='dev', use_aad=True)
    assert config.use_aad
    assert isinstance(config._aad_client, AADClient)
    assert config.accesskey == 'Bearer abcd'
    assert config.username == '123456789'
    assert config.url.startswith('http://127.0.0.1')
    # not testing AADClient, avoid stack trace
    atexit.unregister(write_cache_to_file)


def test_aad_data_plane(temp_dot_bonsai):
    config = Config(argv=sys.argv, profile='dev', use_aad=False)
    assert not config.use_aad
    assert config._aad_client is None
    assert config.accesskey == '00000000-1111-2222-3333-000000000001'
    assert config.username == 'admin'
    assert config.url.startswith('http://127.0.0.1')


if __name__ == '__main__':
    pytest.main([__file__])
