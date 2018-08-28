# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=missing-docstring
# pylint: disable=too-many-function-args
from bonsai_ai.event import SimulateEvent, EpisodeStartEvent, \
    EpisodeFinishEvent, FinishedEvent, UnknownEvent
from tornado import gen


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


def test_server_error(train_sim, monkeypatch):
    # monkeypatched `Simulator._connect` triggers `BonsaiServerError`,
    # which gets logged and percolated through `Simulator.get_next_event`
    # in the form of a `FinishedEvent`
    @gen.coroutine
    def _connect(*args, **kwargs):
        raise gen.Return("Couldn't connect...")
    monkeypatch.setattr(train_sim._impl, '_connect', _connect)
    assert isinstance(train_sim.get_next_event(), FinishedEvent)
