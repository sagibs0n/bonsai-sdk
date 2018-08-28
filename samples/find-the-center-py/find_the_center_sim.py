""" This Basic simulator is for learning the simulator interface.
It can be used in this case to find the center between two numbers.
"""
import bonsai_ai
from random import randint
from time import clock


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

        self.record_append({"goal_count": self.goal_count}, "ftc")
        # is this episode finished?
        terminal = (self.value < self.min or
                    self.value > self.max or
                    self.goal_count > 3)
        state = {"value": self.value}
        reward = self.goal_count
        return (state, reward, terminal)

    def episode_finish(self):
        print('Episode', self.episode_count,
              'reward:', self.episode_reward,
              'eps:', self.episode_rate,
              'ips:', self.iteration_rate,
              'iters:', self.iteration_count)


if __name__ == "__main__":
    config = bonsai_ai.Config()
    # Analytics recording can be enabled in code or at the command line.
    # The commented lines would have the same effect as invoking this
    # script with "--record=find_the_center.json".
    # Alternatively, invoking with "--record=find_the_center.csv" enables
    # recording to CSV.
    # config->set_record_enabled(true);
    # config->set_record_file("find_the_center.json");

    brain = bonsai_ai.Brain(config)

    sim = BasicSimulator(brain, "find_the_center_sim")
    sim.enable_keys(["delta_t", "goal_count"], "ftc")

    print('starting...')
    last = clock() * 10000000
    while sim.run():
        now = clock() * 1000000
        sim.record_append(
            {"delta_t": now - last}, "ftc")
        last = clock() * 1000000
        continue
