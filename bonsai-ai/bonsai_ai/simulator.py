# Copyright (C) 2018 Bonsai, Inc.

import abc

from tornado.ioloop import IOLoop

from bonsai_ai.exceptions import BonsaiClientError, SimStateError, \
    BonsaiServerError
from bonsai_ai.logger import Logger
from bonsai_ai.simulator_ws import Simulator_WS

log = Logger()

_CONNECT_TIMEOUT_SECS = 60


class Simulator(object):
    """
    This class is used to interface with the server while training or
    running predictions against a BRAIN. It is an abstract base class,
    and to use it a developer must create a subclass.

    The `Simulator` class is closely related to the Inkling file that
    is associated with the BRAIN. The name used to construct `Simulator`
    must match the name of the simulator in the Inkling file.

    There are two main methods that you must override, `episode_start`
    and `simulate`. At the start of a session, `episode_start` is called
    once, then `simulate` is called repeatedly until the `terminal` flag is
    returned as `True` or the next `episode_start` interrupts the simulation.

    Attributes:
        brain:          The BRAIN to connect to.
        name:           The name of this Simulator. Must match simulator
                        in Inkling.
        objective_name: The name of the current objective for an episode.

    Example Inkling:
        simulator my_simulator(Config)
            action (Action)
            state (State)
        end

    Example Code:
        class MySimulator(bonsai_ai.Simulator):
            def __init__(brain, name):
                super().__init__(brain, name)
                # your sim init code goes here.

            def episode_start(self, parameters=None):
                # your reset/init code goes here.
                return my_state

            def simulate(self, action):
                # your simulation stepping code goes here.
                return (my_state, my_reward, is_terminal)

        ...

        config = bonsai_ai.Config(sys.argv)
        brain = bonsai_ai.Brain(config)
        sim = MySimulator(brain, "my_simulator")

        while sim.run():
            continue

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, brain, name):
        """
        Constructs the Simulator class.

        Arguments:
            brain: The BRAIN you wish to train or predict against.
            name:  The Simulator name. Must match the name in Inkling.
        """
        self.name = name
        self.brain = brain
        self._ioloop = IOLoop.current()
        self._impl = Simulator_WS(brain, self, name)

    def __repr__(self):
        """ Return a JSON representation of the Simulator. """
        return '{{'\
            'name: {self.name!r}, ' \
            'objective_name: {self._impl.objective_name!r}, ' \
            'predict: {self.predict!r}, ' \
            'brain: {self.brain!r}' \
            '}}'.format(self=self)

    @property
    def predict(self):
        """ True if simulation is configured for prediction. """
        return self.brain.config.predict

    @property
    def objective_name(self):
        """ Current episode objective name. """
        return self._impl.objective_name

    @abc.abstractmethod
    def episode_start(self, episode_config):
        """
        Called at the start of each new episode. This callback passes in a
        set of initial parameters and expects an initial state in return for
        the simulator. Before this callback is called, the property
        `objective_name` will be updated to reflect the current objective
        for this episode.

        This call is where a simulation should be reset for the next round.

        Arguments:
            episode_config: A dict of config paramters defined in Inkling.

        Returns:
            A dictionary of the initial state of the simulation as defined
            in inkling.

        Example Inkling:
            schema Config
                UInt8 start_angle
            end

            schema State
                Float32 angle,
                Float32 velocity
            end

        Example Code:
            def episode_start(self, params):
                # training params are only passed in during training
                if self.predict == False:
                    print(self.objective_name)
                    self.angle = params.start_angle

                initial = {
                    "angle": self.angle,
                    "velocity": self.velocity,
                }
                return initial
        """
        return {}  # initial_state

    @abc.abstractmethod
    def simulate(self, action):
        """
        This callback steps the simulation forward by a single step.
        It passes in the `action` to be taken, and expects the resulting
        `state`, `reward` for the current `objective`, and a `terminal` flag
        used to signal the end of an episode. Note that an episode may be
        reset prematurely by the backend during training.

        For a multi-lesson curriculum, the `objective_name` will change from
        episode to episode. In this case ensure that the simulator is
        returning the correct reward for the different lessons.

        Returning `True` for the `terminal` flag signals the start of a
        new episode.

        Arguments:
            action:     A dict as defined in Inkling of the action to take.

        Returns:
            A tuple of (state, reward, terminal).
            state:    A dict as defined in Inkling of the sim state.
            reward:   A real number describing the reward for this step.
            terminal: True if the simulation has ended or terminated. False
                      if it should continue.

        Example Inkling:
            schema Action
                Int8{0, 1} delta
            end

        Example Code:
            def simulate(self, action):
                velocity = velocity - action.delta;
                terminal = (velocity <= 0.0)

                # reward is only needed during training
                if self.predict == False:
                    reward = reward_for_objective(self.objective_name)

                state = {
                    "velocity": self.velocity,
                    "angle": self.angle,
                }
                return (state, reward, terminal)
        """
        return {}  # state, reward, terminal

    def standby(self, reason):
        log.info(reason)

    def run(self):
        """
        Main loop call for driving the simulation. Returns `False` when the
        simulation has finished or halted.

        The client should call this method in a `while` loop until it
        returns `False`. To run for prediction, `brain.config.predict`
        must return `True`.

        Example:
            sim = MySimulator(brain)

            if sim.predict:
                print("Predicting against ", brain.name,
                      " version ", brain.version)
            else:
                print("Training ", brain.name)

            while sim.run():
                continue
        """
        try:
            success = self._ioloop.run_sync(self._impl.run, 1000)
        except KeyboardInterrupt:
            success = False
        except BonsaiClientError as e:
            log.error(e)
            raise e.original_exception
        except BonsaiServerError as e:
            log.error(e)
            success = False
        except SimStateError as e:
            log.error(e)
            raise e

        return success
