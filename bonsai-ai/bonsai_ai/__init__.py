# Copyright (C) 2018 Bonsai, Inc.

# pylint: disable=wildcard-import

"""
Bonsai Simulator Library.

This module provides the interface for connecting simulators to the Bonsai
system. It is used to train a simulation against a BRAIN.

Classes:
    Config:    A class for managing server and simulation
               configuration information.
    Brain:     A class for talking with a specific BRAIN.
    Simulator: A class for connecting an existing simulation such that it may
               be used to train and predict against a BRAIN.
    Predictor: A class for running predictions against a BRAIN.
    Luminance: A class for representing Luminance data in Inkling schemas.
"""
from .brain import Brain
from .config import Config
from .simulator import Simulator
from .inkling_types import Luminance
from .predictor import Predictor
from .event import EpisodeStartEvent, SimulateEvent, \
    EpisodeFinishEvent, FinishedEvent, UnknownEvent
from .version import __version__
