Bonsai Gym Common
=================
A python library for integrating Bonsai BRAIN with Open AI Gym environments.


Installation
------------

Install the latest stable from PyPI:

`$ pip install bonsai-gym`


Usage
-----
Once installed, import `bonsai_gym` in order to access
base class `GymSimulator`, which implements all of the
environment-independent Bonsai SDK integrations necessary to
train a Bonsai BRAIN to play an OpenAI Gym simulator.

::

    import gym

    from bonsai_gym import GymSimulator

    class CartPoleSimulator(GymSimulator):
        # Perform cartpole-specific integrations here.
