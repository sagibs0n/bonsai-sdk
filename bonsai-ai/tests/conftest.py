# Copyright (C) 2018 Bonsai, Inc.

from __future__ import print_function
import os
import pytest
import requests
import time
from tempfile import mkdtemp
from shutil import rmtree
from tornado.ioloop import IOLoop

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


from bonsai_ai import Simulator, Brain, Config, Luminance, Predictor
from ws import open_bonsai_ws, close_bonsai_ws, set_predict_mode, \
    set_flaky_mode, reset_count, set_fail_duration


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


@pytest.fixture(autouse=True)
def mock_get(monkeypatch, request):
    def _get(*args, **kwargs):
        response = Mock()
        test_json = {'versions': [{'version': 1}],
                     'state': 'In Progress'}
        response.json.return_value = test_json
        return response
    monkeypatch.setattr(requests, 'get', _get)


@pytest.fixture
def v2_get(monkeypatch):
    def _get(*args, **kwargs):
        response = Mock()
        test_json = {'versions': [{'version': 4}],
                     'state': 'Stopped'}
        response.json.return_value = test_json
        return response
    monkeypatch.setattr(requests, 'get', _get)


@pytest.fixture
def blank_brain():
    config = Config([__name__])
    return Brain(config)


@pytest.fixture
def record_json_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://localhost:8889',
        '--brain=cartpole',
        '--proxy=VALUE',
        '--record=foobar.json'
    ])


@pytest.fixture
def record_csv_config():
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://localhost:8889',
        '--brain=cartpole',
        '--proxy=VALUE',
        '--record=foobar.csv'
    ])


@pytest.fixture
def record_csv_config_predict():
    set_predict_mode(True)
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://localhost:8889',
        '--brain=cartpole',
        '--proxy=VALUE',
        '--record=foobar.csv',
        '--predict=4'
    ])


@pytest.fixture
def train_config():
    set_flaky_mode(False)
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://localhost:8889',
        '--brain=cartpole',
        '--proxy=VALUE',
    ])


@pytest.fixture
def flaky_train_config():
    set_flaky_mode(True)
    set_fail_duration(15)
    reset_count()
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://localhost:8889',
        '--brain=cartpole',
        '--proxy=VALUE',
    ])


@pytest.fixture
def predict_config():
    set_predict_mode(True)
    set_flaky_mode(False)
    return Config([
        __name__,
        '--accesskey=VALUE',
        '--username=alice',
        '--url=http://localhost:8889',
        '--brain=cartpole',
        '--proxy=VALUE',
        '--predict=4',
    ])


@pytest.fixture
def logging_config():
    Config([
        __name__,
        '--log', 'foo', 'baz'
    ])


@pytest.fixture
def record_json_sim(record_json_config):
    brain = Brain(record_json_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def record_csv_sim(record_csv_config):
    brain = Brain(record_csv_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def record_csv_predict(record_csv_config_predict):
    brain = Brain(record_csv_config_predict)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def train_sim(train_config):
    brain = Brain(train_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def flaky_train_sim(flaky_train_config):
    brain = Brain(flaky_train_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def predict_sim(predict_config):
    brain = Brain(predict_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def sequence_sim(train_config):
    brain = Brain(train_config)
    sim = SequencingSim(brain, 'cartpole_simulator')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def pr_sequence_sim(predict_config):
    brain = Brain(predict_config)
    sim = SequencingSim(brain, 'cartpole_simulator')
    sim._ioloop = IOLoop.current()
    return sim


@pytest.fixture
def predictor(predict_config):
    brain = Brain(predict_config)
    predictor = Predictor(brain, 'cartpole_simulator')
    predictor._ioloop = IOLoop.current()
    return predictor


@pytest.fixture
def predictor_with_train_config(train_config):
    brain = Brain(train_config)
    predictor = Predictor(brain, 'cartpole_simulator')
    predictor._ioloop = IOLoop.current()
    return predictor


@pytest.fixture
def luminance_sim(train_config):
    brain = Brain(train_config)
    sim = LuminanceSim(brain, 'random_simulator')
    sim._ioloop = IOLoop.current()
    return sim


def pytest_addoption(parser):
    parser.addoption("--protocol", action="store",
                     help="Path to message JSON")


@pytest.fixture(scope='module', autouse=True)
def bonsai_ws(request):
    default_protocol = "{}/proto_bin/cartpole_wire.json".format(
                           os.path.dirname(__file__))

    # default protocol can be overriden at the module level
    protocol = getattr(request.module, 'protocol_file', default_protocol)

    # .. and the command line option has the highest precedence
    if request.config.getoption('--protocol'):
        protocol = request.config.getoption('--protocol')
    server = open_bonsai_ws(protocol)

    def fin():
        close_bonsai_ws()
        server.stop()
    request.addfinalizer(fin)
    return server


@pytest.yield_fixture(scope='module')
def temp_dot_bonsai():
    """
    This fixture creates a temporary directory and writes
    a Config profiles to the disk. The tests that require
    checking parameters in these profiles should use this fixture
    """
    temp_dir = mkdtemp()
    home_dir = os.environ["HOME"] if "HOME" in os.environ else ""
    os.environ["HOME"] = temp_dir

    config = Config()
    config._update(profile='dev',
                   username='admin',
                   accesskey='00000000-1111-2222-3333-000000000001',
                   url='http://localhost')

    yield

    os.environ["HOME"] = home_dir
    rmtree(temp_dir)


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
