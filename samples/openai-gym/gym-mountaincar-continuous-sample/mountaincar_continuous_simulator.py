import sys
import numpy
import logging
from bonsai_ai import Brain, Config
from bonsai_gym import GymSimulator

log = logging.getLogger('gym_simulator')
log.setLevel(logging.DEBUG)


SKIP_FRAME = 4


class MountainCarContinuous(GymSimulator):
    environment_name = 'MountainCarContinuous-v0'
    simulator_name = 'mountaincar_continuous_simulator'

    def gym_to_state(self, observation):
        state = {'x_position': observation[0],
                 'x_velocity': observation[1]}
        return state

    # As an Estimator, continuous mountaincar returns the command
    # as a numpy array.
    def action_to_gym(self, actions):
        # return actions['command']
        return numpy.asarray([actions['command']])


if __name__ == '__main__':
    # create a brain, openai-gym environment, and simulator
    config = Config(sys.argv)
    brain = Brain(config)
    sim = MountainCarContinuous(
        brain, skip_frame=SKIP_FRAME)
    sim.run_gym()
