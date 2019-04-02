# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
import pytest
from conftest import CartSim
import time

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from typing import Any, cast

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


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


# this test raises a runtimewarning around a misused coroutine.
# removing as not meaningful
# def test_sim_run(train_sim):
#     train_sim._ioloop = Mock()
#     train_sim._ioloop.run_until_complete.return_value = True
#     assert train_sim.run() is True

#     train_sim.close()


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


if __name__ == '__main__':
    pytest.main([__file__])
