# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
from bonsai_ai.event import SimulateEvent, EpisodeStartEvent, \
    EpisodeFinishEvent, FinishedEvent, UnknownEvent


def test_event_pump(train_sim):
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
    assert isinstance(train_sim.get_next_event(), EpisodeStartEvent)
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), EpisodeFinishEvent)
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
    assert isinstance(train_sim.get_next_event(), EpisodeStartEvent)
    assert isinstance(train_sim.get_next_event(), SimulateEvent)


def test_server_error(flaky_train_sim):
    flaky_train_sim._impl._sim_connection._retry_timeout_seconds = 0
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), EpisodeStartEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), EpisodeFinishEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), EpisodeStartEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), FinishedEvent)


def test_unable_to_connect_no_operation(flaky_train_sim):
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), EpisodeStartEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), EpisodeFinishEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), EpisodeStartEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), SimulateEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
    assert isinstance(flaky_train_sim.get_next_event(), UnknownEvent)
