import sys
import gym
from bonsai_ai import Brain, Config, Predictor
from bonsai_ai.logger import Logger

log = Logger()
log.set_enabled("info")


def _state(observation):
    """ Converts gym observation into Inkling state dictionary """
    state = {'position': observation[0],
             'velocity': observation[1],
             'angle':    observation[2],
             'rotation': observation[3]}
    return state


def _action(action):
    """ Converts Inkling action into a gym action """
    return action['command']


def _log_state_and_action(state, action):
    log.info("The BRAIN received the following state: {}".format(state))
    log.info("The BRAIN returned the following action: {}".format(action))


if __name__ == '__main__':
    # Set up predictor
    config = Config(sys.argv)
    brain = Brain(config)
    predictor = Predictor(brain, 'cartpole_simulator')

    # Set up cartpole simulator
    episode_count = 10
    env = gym.make('CartPole-v0')

    # Reset, get state, exchange state for action, and then step the sim
    observation = env.reset()
    state = _state(observation)
    action = _action(predictor.get_action(state))
    _log_state_and_action(state, action)
    observation, reward, done, info = env.step(action)
    env.render()

    # Loop until episode_count is reached
    while episode_count:
        state = _state(observation)
        action = _action(predictor.get_action(state))
        _log_state_and_action(state, action)
        observation, reward, done, info = env.step(action)
        env.render()

        if done:
            episode_count -= 1
            observation = env.reset()
