# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
import pytest

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai.common.state_to_proto import SimStateError
from bonsai_ai.exceptions import BonsaiServerError


def test_predictor(predictor, bonsai_ws):
    state = {'position': 0,
             'velocity': 0,
             'angle':    0,
             'rotation': 0}

    with predictor:
        assert predictor._impl._prev_message_type == \
            ServerToSimulator.UNKNOWN

        action = predictor.get_action(state)
        assert action is not None
        assert predictor._impl._prev_message_type == \
            ServerToSimulator.PREDICTION


def test_predictor_invalid_state(predictor, bonsai_ws):
    try: 
        state = {'FOO': 0,
                 'BAR': 0,
                 'CART': 0,
                 'POLE': 0}

        with predictor:
            assert predictor._impl._prev_message_type == \
                ServerToSimulator.UNKNOWN
            predictor.get_action(state)
    except SimStateError as e:
        return

    assert False, "XFAIL"


def test_predictor_with_train_config(predictor_with_train_config, capsys):
    with predictor_with_train_config:
        predictor_with_train_config.get_action(None)
    out, err = capsys.readouterr()
    assert 'Error while connecting to websocket' in err
    predictor_with_train_config.close()


def test_predictor_predict_flag(predictor):
    assert predictor.predict is True
