""" This Basic simulator is for learning the simulator interface.
It can be used in this case to find the center between two numbers.
"""
import bonsai_ai
from random import randint


class BasicSimulator(bonsai_ai.Simulator):
    """ A basic simulator class that takes in a move from the inkling file,
    and returns the state as a result of that move.
    """
    min = 0
    max = 2
    goal = 1
    started = False

    def episode_start(self, parameters=None):
        """ called at the start of every episode. should
        reset the simulation and return the initial state
        """

        # reset internal initial state
        self.goal_count = 0
        self.value = randint(self.min, self.max)

        # print out a message for our first episode
        if not self.started:
            self.started = True
            print('started.')

        # return initial external state
        return {"value": self.value}

    def simulate(self, action):
        """ run a single step of the simulation.
        if the simulation has reached a terminal state, mark it as such.
        """

        # perform the action
        self.value += action["delta"]
        if self.value == self.goal:
            self.goal_count += 1

        # is this episode finished?
        terminal = (self.value < self.min or
                    self.value > self.max or
                    self.goal_count > 3)
        state = {"value": self.value}
        reward = self.goal_count
        return (state, reward, terminal)


if __name__ == "__main__":
    config = bonsai_ai.Config()
    brain = bonsai_ai.Brain(config)
    sim = BasicSimulator(brain, "find_the_center_sim")

    print('starting...')
    while sim.run():
        continue
