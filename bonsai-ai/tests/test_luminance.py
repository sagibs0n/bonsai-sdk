# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args

import os
import pytest
from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai.proto.generator_simulator_api_pb2 import SimulatorToServer

try:
    from math import isclose
except ImportError:
    from conftest import isclose

from struct import unpack


protocol_file = "{}/proto_bin/luminance_wire.json".format(
                    os.path.dirname(__file__))


def test_luminance_sim(luminance_sim):
    assert luminance_sim.run() is True
    assert luminance_sim._impl._prev_message_type == \
        ServerToSimulator.ACKNOWLEDGE_REGISTER

    assert luminance_sim.run() is True
    assert luminance_sim._impl._prev_message_type == \
        ServerToSimulator.SET_PROPERTIES

    assert luminance_sim.run() is True
    assert luminance_sim._impl._prev_message_type == \
        ServerToSimulator.START

    assert luminance_sim.run() is True
    assert luminance_sim._impl._prev_message_type == \
        ServerToSimulator.PREDICTION

    assert luminance_sim.run() is True
    assert luminance_sim._impl._prev_message_type == \
        ServerToSimulator.STOP

    assert luminance_sim.run() is True
    assert luminance_sim._impl._prev_message_type == \
        ServerToSimulator.RESET


def test_luminance_pack(luminance_sim):
    # run uninterrupted until we hit a prediction
    while luminance_sim._impl._prev_message_type != \
          ServerToSimulator.PREDICTION:
        assert luminance_sim.run() is True

    # process incoming predictions manually
    for step in luminance_sim._impl._sim_steps:
        luminance_sim._impl._advance(step)

    # pack the resulting states into a message for the server, serialize
    # it, but don't send it
    to_server = SimulatorToServer()
    luminance_sim._impl._on_send(to_server)
    out_bytes = to_server.SerializeToString()
    assert out_bytes is not None

    # instead, parse it back out into a message (should be identical)
    from_sim = SimulatorToServer()
    from_sim.ParseFromString(out_bytes)
    assert from_sim == to_server

    # grab a dynamic state message and use it to construct an inkling
    # message
    state_message = from_sim.state_data[0].state
    msg = luminance_sim._impl._inkling.message_for_dynamic_message(
        state_message, luminance_sim._impl._output_schema)

    # finally, confirm that the "incoming" luminance object matches
    # the one constructed in the simulator
    lum = msg.pixels
    pixels = unpack('%sf' % lum.height * lum.width, lum.pixels)
    assert lum.width == luminance_sim.width
    assert lum.height == luminance_sim.height
    assert len(pixels) == len(luminance_sim.STATE_PIXELS)
    for p1, p2 in zip(pixels, luminance_sim.STATE_PIXELS):
        assert isclose(p1, p2)
