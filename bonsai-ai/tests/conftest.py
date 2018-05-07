# Copyright (C) 2018 Bonsai, Inc.

import os
import pytest
import requests
import time

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


from bonsai_ai import Simulator, Brain, Config, Luminance, Predictor
from ws import open_bonsai_ws, close_bonsai_ws


class CartSim(Simulator):
    def episode_start(self, parameters):
        print('episode_start:', parameters)
        self.record_append({'foo': 23}, 'bar')
        initial = {
            "position": 1.0,
            "velocity": 0.0,
            "angle": 0.0,
            "rotation": 0.0
        }
        return initial

    def simulate(self, action):
        print('simulate:', action)
        self.record_append({'foo': 23}, 'bar')
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


@pytest.fixture(autouse=True)
def mock_get(monkeypatch):
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
        test_json = {'versions': [{'version': 2}],
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
def train_config():
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
    return sim


@pytest.fixture
def record_csv_sim(record_csv_config):
    brain = Brain(record_csv_config)
    sim = CartSim(brain, 'cartpole_simulator')
    sim.enable_keys(['foo'], 'bar')
    return sim


@pytest.fixture
def train_sim(train_config):
    brain = Brain(train_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def predict_sim(predict_config):
    brain = Brain(predict_config)
    sim = CartSim(brain, 'cartpole_simulator')
    return sim


@pytest.fixture
def predictor(predict_config):
    brain = Brain(predict_config)
    predictor = Predictor(brain, 'cartpole_simulator')
    return predictor


@pytest.fixture
def predictor_with_train_config(train_config):
    brain = Brain(train_config)
    predictor = Predictor(brain, 'cartpole_simulator')
    return predictor


@pytest.fixture
def luminance_sim(train_config):
    brain = Brain(train_config)
    sim = LuminanceSim(brain, 'random_simulator')
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


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
