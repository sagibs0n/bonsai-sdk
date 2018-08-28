import sys
import logging
from bonsai_ai import Brain, Config
from bonsai_gym import GymSimulator

log = logging.getLogger('gym_simulator')
log.setLevel(logging.DEBUG)


class CartPole(GymSimulator):
    # Environment name, from openai-gym
    environment_name = 'CartPole-v0'

    # simulator name from Inkling
    # Example Inkling:
    #   curriculum balance_curriculum
    #       train balance
    #       with simulator cartpole_simulator
    #       ....
    simulator_name = 'cartpole_simulator'

    # convert openai gym observation to our state schema
    # Example Inkling:
    #   schema GameState
    #       Float32 position,
    #       Float32 velocity,
    #       Float32 angle,
    #       Float32 rotation
    #   end
    def gym_to_state(self, observation):
        state = {'position': observation[0],
                 'velocity': observation[1],
                 'angle':    observation[2],
                 'rotation': observation[3]}
        return state

    # convert our action schema into openai gym action
    # Example Inkling:
    #   schema Action
    #       Int8{0, 1} command
    #   end
    def action_to_gym(self, action):
        return action['command']


if __name__ == '__main__':
    # create a brain, openai-gym environment, and simulator
    config = Config(sys.argv)
    brain = Brain(config)
    sim = CartPole(brain)
    sim.run_gym()
