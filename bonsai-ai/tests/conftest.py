# Copyright (C) 2018 Bonsai, Inc.

from __future__ import print_function
import os
import sys
import pytest
import requests
import time
from tempfile import mkdtemp
from shutil import rmtree
from urllib.parse import urlparse

from aiohttp import web
from multiprocessing import Process
from socket import AF_INET, SOCK_STREAM, socket
from typing import Any, cast
from uuid import uuid4

# pytest-server-fixtures module doesn't support Windows
# pytest-server-fixtures may need more configuration for OSX support
if os.name == 'posix' and sys.platform != 'darwin':
    from pytest_server_fixtures.httpd import HTTPDServer
else:
    HTTPDServer = None

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


from bonsai_ai import Simulator, Brain, Config, Luminance, Predictor, \
    BrainController
from bonsai_ai.brain_api import BrainAPI
from ws_aiohttp import open_bonsai_ws


def tgt(protocol):
    the_app = open_bonsai_ws(protocol)
    web.run_app(app=the_app, host="127.0.0.1", port=9000)


class CartSim(Simulator):
    def episode_start(self, parameters):
        print('episode_start:', parameters)
        initial = {
            "position": 1.0,
            "velocity": 0.0,
            "angle": 0.0,
            "rotation": 0.0
        }
        return initial

    def simulate(self, action):
        print('simulate:', action)
        terminal = True
        state = {
            "position": 1.0,
            "velocity": 0.0,
            "angle": 0.0,
            "rotation": 0.0
        }
        return (state, 1.0, terminal)

    def standby(self, reason):
        print('standby:' + reason)
        time.sleep(1)
        return True


class LuminanceSim(Simulator):
    width = 2
    height = 3

    STATE_PIXELS = [0, -1, 1000, 1, 2, 3]

    def episode_start(self, parameters):
        parameters['pixels'] = Luminance(
            self.width, self.height, [0, 1, 2, 3, 4, 5])

        print('episode_start: ', parameters['pixels'])
        initial = {
            "pixels": Luminance(
                self.width, self.height, self.STATE_PIXELS)
        }
        return initial

    def simulate(self, action):
        print('simulate: ', action)
        terminal = True

        state = {
            "pixels": Luminance(
                self.width, self.height, [0, -1, 1000, 1, 2, 3])
        }

        return (state, 1.0, terminal)

    def standby(self, reason):
        print('standby:' + reason)
        time.sleep(1)
        return True


class SequencingSim(Simulator):
    def __init__(self, brain, name):
        super(SequencingSim, self).__init__(brain, name)
        self.last_step_type = None
        self._n = 0
        self._ep_start_called = False

    def _generate_terminal(self):
        self._n += 1
        if self._n % 5 == 0:
            yield 1
        elif self._n % 2 == 0:
            yield 1
        else:
            yield 0

    def episode_start(self, parameters):
        self._ep_start_called = True
        print('\n\nES{}'.format(self.episode_count), end=' ')
        assert(self.last_step_type is None or
               self.last_step_type == 'F')
        self.last_step_type = 'E'

        initial = {
            "position": 1.0,
            "velocity": 0.0,
            "angle": 0.0,
            "rotation": 0.0
        }
        return initial

    def simulate(self, action):
        # fail if episode_start has *never* been called
        assert(self._ep_start_called)
        state = {
            "position": 1.0,
            "velocity": 0.0,
            "angle": 0.0,
            "rotation": 0.0
        }

        # Randomly return terminal condition
        terminal = next(self._generate_terminal())
        if terminal:
            # Test for double terminate calls
            print('T{}'.format(self.iteration_count), end=' ')
            assert(self.last_step_type != 'T')
            self.last_step_type = 'T'
        else:
            # Test for terminal before step
            print('S{}'.format(self.iteration_count), end=' ')
            assert(self.last_step_type != 'T')
            self.last_step_type = 'S'

        return (state, 1.0, terminal)

    def episode_finish(self):
        print('F', end=' ')
        # previous step can be a Terminal, Step or EStart
        # but not another finished
        assert(self.last_step_type != 'F')
        self.last_step_type = 'F'

    def standby(self, reason):
        print('standby:' + reason)
        time.sleep(1)
        return True


@pytest.fixture
def mock_get(monkeypatch, request):
    def _get(*args, **kwargs):
        response = cast(Any, Mock())
        test_json = {'versions': [{'version': 1}],
                     'state': 'In Progress'}
        response.json.return_value = test_json
        return response
    monkeypatch.setattr(requests.Session, 'get', _get)


@pytest.fixture
def v2_get(monkeypatch):
    def _get(*args, **kwargs):
        response = cast(Any, Mock())
        test_json = {'versions': [{'version': 4}],
                     'state': 'Stopped'}
        response.json.return_value = test_json
        return response
    monkeypatch.setattr(requests.Session, 'get', _get)


@pytest.fixture
def request_errors(request, monkeypatch):
    error = None
    response = None
    if request.param == 'connection':
        error = requests.exceptions.ConnectionError
    elif request.param == 'timeout':
        error = requests.exceptions.Timeout
    elif request.param == 'http':
        response = cast(Any, Mock())
        response.raise_for_status = Mock(
            side_effect=requests.exceptions.HTTPError(503))
        response.json = Mock(side_effect=ValueError)
        response.headers = {'SpanID': uuid4()}

    def _request_error(*args, **kwargs):
        if error:
            raise error
        else:
            return response

    monkeypatch.setattr(requests.Session, 'get', _request_error)
    monkeypatch.setattr(requests.Session, 'put', _request_error)
    monkeypatch.setattr(requests.Session, 'delete', _request_error)
    monkeypatch.setattr(requests.Session, 'post', _request_error)


@pytest.yield_fixture()
def proxy_server():
    proxy_rules = {'/': 'http://127.0.0.1:9000/'}
    extra_cfg = """
    LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so
    LoadModule proxy_wstunnel_module /usr/lib/apache2/modules/mod_proxy_wstunnel.so

    ServerName localhost
    LogLevel debug
    Mutex pthread

    RewriteEngine on
    RewriteCond %{HTTP:UPGRADE} ^WebSocket$$ [NC]
    RewriteCond %{HTTP:CONNECTION} ^Upgrade$$ [NC]
    RewriteRule .* ws://127.0.0.1:9000%{REQUEST_URI} [P]
    """
    if not HTTPDServer:
        raise Exception('This module works only on posix platforms')
    server = HTTPDServer(proxy_rules,
                         extra_cfg=extra_cfg,
                         log_dir='/brain/src/sdk2/bonsai-ai')
    server.start()
    yield server
    server.teardown()


@pytest.fixture
def blank_brain(mock_get):
    config = Config([__name__])
    return Brain(config)


@pytest.fixture
def record_json_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--record=foobar.json',
        '--disable-telemetry',
    ])


@pytest.fixture
def record_csv_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--record=foobar.csv',
        '--disable-telemetry',
    ])


@pytest.fixture
def record_csv_config_predict():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--record=foobar.csv',
        '--predict=4',
        '--disable-telemetry',
    ])


@pytest.fixture
def train_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def train_config_proxy_pair(proxy_server):
    config = Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--proxy={}'.format(proxy_server.uri),
        '--brain=cartpole',
        '--disable-telemetry',
    ])
    return {'config': config, 'log_dir': proxy_server.log_dir}


@pytest.fixture
def train_config_bad_proxy(proxy_server):
    tcp = socket(AF_INET, SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    free_port = str(port)
    parsed_uri = urlparse(proxy_server.uri)
    bad_uri = proxy_server.uri.replace(str(parsed_uri.port), free_port)
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--proxy={}'.format(bad_uri),
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def auth_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=needsauth',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def flaky_train_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=flake',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def eofstream_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=eofstream',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def error_msg_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=error_msg',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def pong_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=pong',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--disable-telemetry',
    ])


@pytest.fixture
def predict_config():
    # set_flaky_mode(False)
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://127.0.0.1:9000',
        '--brain=cartpole',
        '--predict=4',
        '--disable-telemetry',
    ])


@pytest.fixture
def logging_config():
    Config([
        __name__,
        '--log', 'foo', 'baz',
        '--disable-telemetry',
    ])


@pytest.fixture
def record_json_sim(record_json_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(record_json_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    return sim


@pytest.fixture
def record_csv_sim(record_csv_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(record_csv_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    return sim


@pytest.fixture
def record_csv_predict(record_csv_config_predict):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(record_csv_config_predict)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    return sim


@pytest.fixture
def train_sim_proxy_pair(train_config_proxy_pair, request):
    requests.patch("{}/cartpole".format(
        train_config_proxy_pair['config'].proxy))
    brain = Brain(train_config_proxy_pair['config'])
    sim = CartSim(brain, 'cartpole_simulator')
    return {'sim': sim, 'log_dir': train_config_proxy_pair['log_dir']}


@pytest.fixture
def train_sim_bad_proxy(train_config_bad_proxy, request):
    brain = Brain(train_config_bad_proxy)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def train_sim(train_config, request):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(train_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def auth_sim(auth_config, request):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(auth_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def flaky_train_sim(flaky_train_config, request):
    requests.patch("http://127.0.0.1:9000/reset")
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(flaky_train_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def eofstream_sim(eofstream_config, request):
    requests.patch("http://127.0.0.1:9000/reset")
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(eofstream_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def error_msg_sim(error_msg_config, request):
    requests.patch("http://127.0.0.1:9000/reset")
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(error_msg_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def pong_sim(pong_config, request):
    requests.patch("http://127.0.0.1:9000/reset")
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(pong_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def predict_sim(predict_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(predict_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def sequence_sim(train_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(train_config)
    sim = SequencingSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def pr_sequence_sim(predict_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(predict_config)
    sim = SequencingSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def predictor(predict_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(predict_config)
    predictor = Predictor(brain, 'cartpole_simulator')
    return predictor


@pytest.fixture
def predictor_with_train_config(train_config):
    requests.patch("http://127.0.0.1:9000/cartpole")
    brain = Brain(train_config)
    predictor = Predictor(brain, 'cartpole_simulator')
    return predictor


@pytest.fixture
def luminance_sim(train_config):
    requests.patch("http://127.0.0.1:9000/luminance")
    brain = Brain(train_config)
    sim = LuminanceSim(brain, 'random_simulator')
    return sim


@pytest.fixture
def brain_api(train_config):
    api = BrainAPI(train_config)
    return api


@pytest.fixture
def brain_controller(train_config):
    controller = BrainController(train_config)
    return controller

def pytest_addoption(parser):
    parser.addoption("--protocol", action="store",
                     help="Path to message JSON")


@pytest.fixture(scope='session', autouse=True)
def bonsai_ws(request):
    default_protocol = "{}/proto_bin/cartpole_wire.json".format(
        os.path.dirname(__file__))

    # default protocol can be overriden at the module level
    protocol = getattr(request.session, 'protocol_file', default_protocol)

    # .. and the command line option has the highest precedence
    if request.config.getoption('--protocol'):
        protocol = request.config.getoption('--protocol')

    proc = Process(target=tgt, args=(protocol,))
    proc.daemon = True
    proc.start()
    time.sleep(2)

    def fin():
        proc.terminate()

    request.addfinalizer(fin)


@pytest.yield_fixture(scope='module')
def temp_dot_bonsai():
    """
    This fixture creates a temporary directory and writes
    a Config profiles to the disk. The tests that require
    checking parameters in these profiles should use this fixture
    """
    temp_dir = mkdtemp('')
    home_dir = os.environ["HOME"] if "HOME" in os.environ else ""
    os.environ["HOME"] = temp_dir

    config = Config()
    config._update(profile='dev',
                   username='admin',
                   accesskey='00000000-1111-2222-3333-000000000001',
                   url='http://127.0.0.1')

    yield

    os.environ["HOME"] = home_dir
    rmtree(temp_dir)


@pytest.yield_fixture()
def temp_directory():
    temp_dir = mkdtemp('')
    cur_dir = os.getcwd()
    os.chdir(temp_dir)
    yield
    os.chdir(cur_dir)
    rmtree(temp_dir)


@pytest.yield_fixture()
def temp_home_directory_read_only(temp_directory):
    cur_dir = os.getcwd()
    home_dir = os.environ["HOME"] if "HOME" in os.environ else ""
    os.chmod(cur_dir, 0o444)
    os.environ["HOME"] = cur_dir
    yield
    os.chmod(cur_dir, 0o777)
    os.environ["HOME"] = home_dir


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
