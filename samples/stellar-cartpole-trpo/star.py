"""
This file contains machine teaching logic such as state, terminal, action,
and reward functions.
"""

import math
import random
from bonsai_ai.logger import Logger

log = Logger()

class Star():
    iteration_count = 0
    model_state = None
    steps_beyond_done = None

    def __init__(self):
        # Angle at which to fail the episode
        self.theta_threshold_radians = 12 * 2 * math.pi / 360
        self.x_threshold = 2.4

    def state(self, model_state):
        """ This function converts the simulator state into the state
        representation the brain uses to learn. """
        self.model_state = model_state
        brain_state = {
            'position': model_state[0],
            'velocity': model_state[1],
            'angle': model_state[2],
            'rotation': model_state[3],
        }
        print(brain_state)
        return brain_state

    def terminal(self, model_state):
        """ Terminal conditions specify when to end an episode, typically due
        to success, failure, or running out of time. In this case, we only
        terminate when the pole falls down. """
        print(model_state)
        x, x_dot, theta, theta_dot = model_state
        done = (x < -self.x_threshold or
                x > self.x_threshold or
                theta < -self.theta_threshold_radians or
                theta > self.theta_threshold_radians)
        done = bool(done)
        return done

    def action(self, brain_action):
        """ This function converts the action representation the brain learns
        to use into the action representation the simulator uses to act in the
        simulated environment. """
        self.iteration_count += 1
        model_action = 0
        if brain_action['command'] > 0:
            model_action = 1
        return model_action

    def reward(self, done):
        """ Give the brain feedback on how well it is doing in this episode.
        In this case, this is simply 1 every time period that the pole is
        balanced. The brain's job is to learn to maximize the reward it gets
        during the episode, which corresponds to balancing as long as possible.
        """
        if not done:
            reward = 1.0
        elif self.steps_beyond_done is None:
            # Pole just fell!
            self.steps_beyond_done = 0
            reward = 1.0
        else:
            if self.steps_beyond_done == 0:
                log.info("You are calling 'step()' even though this \
                         environment has already returned done = True. \
                         You should always call 'reset()' once you receive \
                         'done = True' -- any further steps are undefined \
                         behavior.")
            self.steps_beyond_done += 1
            reward = 0.0
        return reward

    def reset(self, model_state):
        self.iteration_count = 0
        brain_state = self.state(model_state)
        self.steps_beyond_done = None

        return brain_state
