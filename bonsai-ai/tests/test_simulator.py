# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
import pytest
from conftest import CartSim

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator

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


def test_sim_run(train_sim):
    train_sim._ioloop = Mock()
    train_sim._ioloop.run_sync.return_value = True
    assert train_sim.run() is True


def test_sim_predict_flag(predict_sim):
    assert predict_sim.predict is True


@pytest.mark.xfail(raises=(TypeError), strict=True)
def test_brain_create_with_invalid_args():
    sim = CartSim()


if __name__ == '__main__':
    pytest.main([__file__])
