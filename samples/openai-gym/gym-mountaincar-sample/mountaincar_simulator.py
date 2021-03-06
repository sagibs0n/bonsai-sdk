import sys
import logging
from bonsai_ai import Brain, Config
from bonsai_gym import GymSimulator

log = logging.getLogger('gym_simulator')
log.setLevel(logging.DEBUG)


SKIP_FRAME = 4


class MountainCar(GymSimulator):
    environment_name = 'MountainCar-v0'
    simulator_name = 'MountainCarSimulator'

    def gym_to_state(self, observation):
        state = {'x_position': observation[0],
                 'x_velocity': observation[1]}
        return state

    def action_to_gym(self, inkling_action):
        return inkling_action['command']


if __name__ == '__main__':
    # create a brain, openai-gym environment, and simulator
    config = Config(sys.argv)
    brain = Brain(config)
    sim = MountainCar(brain, skip_frame=SKIP_FRAME)
    sim.run_gym()
