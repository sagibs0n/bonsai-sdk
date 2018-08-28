import math
import random

from bonsai_ai.logger import Logger


def noise0(var):
    return var


def noise20(var):
    level = random.uniform(.9, 1.1)
    return var*level


def noise40(var):
    level = random.uniform(.8, 1.2)
    return var*level


noise_func = noise0
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
        self.model_state = model_state
        brain_state = {
            'position': noise_func(model_state[0]),
            'velocity': noise_func(model_state[1]),
            'angle': noise_func(model_state[2]),
            'rotation': noise_func(model_state[3]),
        }
        print(brain_state)
        return brain_state

    def terminal(self, model_state):
        print(model_state)
        x, x_dot, theta, theta_dot = model_state
        done = (x < -self.x_threshold or
                x > self.x_threshold or
                theta < -self.theta_threshold_radians or
                theta > self.theta_threshold_radians)
        done = bool(done)
        return done

    def action(self, brain_action):
        self.iteration_count += 1
        model_action = 0
        if brain_action['command'] > 0:
            model_action = 1
        return model_action

    def reward(self, done):
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
