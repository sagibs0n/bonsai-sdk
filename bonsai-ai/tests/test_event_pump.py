# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
from bonsai_ai.event import SimulateEvent, EpisodeStartEvent, \
    EpisodeFinishEvent, FinishedEvent, UnknownEvent
from ws import set_flaky_mode, reset_count


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


def test_server_error(train_sim):
    set_flaky_mode(True)
    reset_count()
    train_sim._impl._sim_connection._retry_timeout_seconds = 0
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
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), FinishedEvent)


def test_unable_to_connect_no_operation(train_sim):
    set_flaky_mode(True)
    reset_count()
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
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), SimulateEvent)
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
    assert isinstance(train_sim.get_next_event(), UnknownEvent)
