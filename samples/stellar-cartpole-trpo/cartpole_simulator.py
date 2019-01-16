"""
This file contains the simulator that controls the cartpole model
using actions from the Bonsai Platform
"""

import sys

import bonsai_ai
import star
from cartpole import CartPole

log = bonsai_ai.logger.Logger()

class CartpoleSimulator(bonsai_ai.Simulator):
    """ A basic simulator class that takes in a move from the inkling file,
    and returns the state as a result of that move.
    """

    def __init__(self, brain, name, config):
        super(CartpoleSimulator, self).__init__(brain, name)
        self.model = None

    def episode_start(self, parameters=None):
        """ called at the start of every episode. should
        reset the simulation and return the initial state
        """
        log.info('Episode {} Starting'.format(self.episode_count))
        self.model.reset()

        return star.state(self.model.state)

    def simulate(self, brain_action):
        """ run a single step of the simulation.
        if the simulation has reached a terminal state, mark it as such.
        """
        action = star.action(brain_action)

        self.model.step(action)

        if self.iteration_count >= 200:
            terminal = True
        else:
            terminal = star.terminal(self.model.state)

        reward = star.reward(self.model.state, terminal)
        brain_state = star.state(self.model.state)

        return (brain_state, reward, terminal)


if __name__ == "__main__":
    config = bonsai_ai.Config(sys.argv)
    brain = bonsai_ai.Brain(config)

    model = CartPole()
    sim = CartpoleSimulator(brain, 'the_simulator', config)
    sim.model = model

    render = None
    if '--render' in sys.argv:
        log.info('rendering')
        from render import Viewer
        render = True
        viewer = Viewer()
        viewer.model = model

    log.info('starting simulation...')
    while sim.run():
        if render:
            viewer.update()
            if viewer.has_exit:
                viewer.close()
                sys.exit(0)

