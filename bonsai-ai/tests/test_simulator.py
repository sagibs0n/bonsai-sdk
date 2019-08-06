# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
import os
import pytest
import sys
import time

from aiohttp.client_exceptions import ClientProxyConnectionError
from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai import Config, Brain, Simulator
from conftest import CartSim
from typing import Any, cast


def test_train(train_sim):
    assert train_sim.run() is True
    assert train_sim._impl._prev_message_type == \
        ServerToSimulator.ACKNOWLEDGE_REGISTER

    assert train_sim.run() is True
    assert train_sim._impl._prev_message_type == \
        ServerToSimulator.SET_PROPERTIES

    assert train_sim.run() is True
    assert train_sim._impl._prev_message_type == \
        ServerToSimulator.START

    for i in range(0, 5):
        assert train_sim.run() is True
        assert train_sim._impl._prev_message_type == \
            ServerToSimulator.PREDICTION

    assert train_sim.run() is True
    assert train_sim._impl._prev_message_type == \
        ServerToSimulator.STOP

    assert train_sim.run() is True
    assert train_sim._impl._prev_message_type == \
        ServerToSimulator.RESET

    train_sim.close()


def test_rate_counter(train_sim):
    assert train_sim._reset_rate_counter is True
    assert train_sim.episode_rate == 0
    assert train_sim.iteration_rate == 0

    # Advance sim to episode_start
    for i in range(0, 3):
        train_sim.run()
    assert train_sim._reset_rate_counter is False
    assert train_sim.iteration_rate == 0
    assert train_sim.episode_rate == 0

    # Advance sim a couple cycles and check rates
    for i in range(0, 20):
        train_sim.run()
    assert train_sim._reset_rate_counter is False
    assert train_sim.iteration_rate != 0
    assert train_sim.episode_rate != 0

    train_sim.close()


def test_predict(predict_sim):
    assert predict_sim.run() is True
    assert predict_sim._impl._prev_message_type == \
        ServerToSimulator.ACKNOWLEDGE_REGISTER

    # run through the whole pile of actions twice to ensure
    # that we stay in the prediction loop
    for i in range(0, 10):
        assert predict_sim.run() is True
        assert predict_sim._impl._prev_message_type == \
            ServerToSimulator.PREDICTION

    predict_sim.close()


def test_reset_rate_counter(train_sim, monkeypatch):
    def _patched_sleep(backoff):
        return backoff
    monkeypatch.setattr(time, 'sleep', _patched_sleep)

    assert train_sim._reset_rate_counter is True
    assert train_sim.episode_rate == 0
    assert train_sim.iteration_rate == 0

    while train_sim.run():
        if train_sim._impl._prev_message_type == ServerToSimulator.START:
            break
    assert train_sim._reset_rate_counter is False
    assert train_sim.iteration_rate == 0
    assert train_sim.episode_rate == 0

    for i in range(0, 20):
        train_sim.run()
    assert train_sim._reset_rate_counter is False
    assert train_sim.iteration_rate != 0
    assert train_sim.episode_rate != 0

    train_sim.close()


@pytest.mark.skipif(sys.platform.startswith('win'), reason='Win not supported')
@pytest.mark.skipif(sys.platform == 'darwin', reason='OSX not supported')
def test_train_proxy(train_sim_proxy_pair):
    train_sim_proxy = train_sim_proxy_pair['sim']
    assert train_sim_proxy.run() is True
    assert train_sim_proxy._impl._prev_message_type == \
        ServerToSimulator.ACKNOWLEDGE_REGISTER

    train_sim_proxy.close()

    proxy_log = os.path.join(train_sim_proxy_pair['log_dir'], 'access.log')
    with open(proxy_log, 'r') as f:
        log_data = f.read()
        entry = 'GET ws://127.0.0.1:9000/v1/alice/cartpole/sims/ws'
        assert entry in log_data


@pytest.mark.skipif(sys.platform.startswith('win'), reason='Win not supported')
@pytest.mark.skipif(sys.platform == 'darwin', reason='OSX not supported')
def test_train_bad_proxy(train_sim_bad_proxy):
    with pytest.raises(ClientProxyConnectionError):
        train_sim_bad_proxy.run()


def test_sim_predict_flag(predict_sim):
    assert predict_sim.predict is True
    predict_sim.close()


def test_brain_create_with_invalid_args():
    try:
        # Intentionally fail to pass parameters
        sim = cast(Any, CartSim)()
    except TypeError as e:
        return

    assert False, "XFAIL"


def test_run_subclass_without_episode_start(train_config):
    class SubClass(Simulator):
        def simulate(self, action):
            return
    try:
        brain = Brain(train_config)
        sim = SubClass(brain, 'cartpole_simulator')
        for _ in range(5):
            sim.run()
    except NotImplementedError:
        return
    assert False, "XFAIL"


def test_run_subclass_without_simulate(train_config):
    class SubClass(Simulator):
        def episode_start(self, action):
            return
    try:
        brain = Brain(train_config)
        sim = SubClass(brain, 'cartpole_simulator')
        for _ in range(5):
            sim.run()
    except NotImplementedError:
        return
    assert False, "XFAIL"


def test_run_simulator_with_no_dot_bonsai_or_cl_args(
        temp_home_directory_read_only, capsys):
    config = Config()
    config.disable_telemetry = True
    brain = Brain(config)
    sim = Simulator(brain, 'sim')
    sim.run()
    captured = capsys.readouterr()
    assert 'Configuration is invalid' in captured.err


def test_run_simulator_no_dot_bonsai(
        train_sim, temp_home_directory_read_only):
    assert train_sim.run() is True


def test_access_sim_id(train_sim):
    assert train_sim.sim_id == ''
    assert train_sim.run() is True
    assert train_sim.sim_id == '270022238'
    train_sim.close()
    assert train_sim.sim_id == '270022238'


if __name__ == '__main__':
    pytest.main([__file__])
