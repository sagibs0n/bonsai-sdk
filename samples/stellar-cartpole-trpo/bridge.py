"""
This file contains the code that bridges the model
with the bonsai platform
"""
import sys

import bonsai_ai
import star
from cartpole import CartPoleModel
from render import _renderer

log = bonsai_ai.logger.Logger()

star = star.Star()
model = CartPoleModel()
the_renderer = None


class ModelConnector(bonsai_ai.Simulator):
    """ A basic simulator class that takes in a move from the inkling file,
    and returns the state as a result of that move.
    """
    info = {}
    started = False
    reward = None
    terminal = None

    def __init__(self, brain, name, config):
        super(ModelConnector, self).__init__(brain, name)

    def episode_start(self, parameters=None):
        """ called at the start of every episode. should
        reset the simulation and return the initial state
        """
        log.info('Episode {} Starting'.format(self.episode_count))
        state = model._reset()
        state = star.reset(state)
        # print out a message for our first episode
        if not self.started:
            self.started = True
            print('started.')

        return state

    def simulate(self, brain_action):
        """ run a single step of the simulation.
        if the simulation has reached a terminal state, mark it as such.
        """
        action = star.action(brain_action)
        (model_state,
         model_reward,
         model_terminal,
         model_info) = model._step(action)
        self.terminal = star.terminal(model_state)
        self.info = model_info
        self.reward = star.reward(model_terminal)
        brain_state = star.state(model_state)

        if the_renderer is not None:
            the_renderer._render()

        return (brain_state, self.reward, self.terminal)

    def get_terminal(self):
        return self.terminal


if __name__ == "__main__":
    config = bonsai_ai.Config(sys.argv)
    brain = bonsai_ai.Brain(config)
    bridge = ModelConnector(brain, 'the_simulator', config)

    if '--render' in sys.argv:
        log.info('rendering')
        the_renderer = _renderer(model)

    log.info('starting simulation...')
    while bridge.run():
        continue
