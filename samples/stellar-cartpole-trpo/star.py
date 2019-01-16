""" The state transform, action transform, terminal function and reward 
    function. The functions in this file are called from cartpolesimulator.py.
"""

import math

from bonsai_ai.logger import Logger

log = Logger()


def state(model_state):
    """ Convert the state as represented in CartPole to a format expected.
        by the AI Engine.
    """
    return {
        'position': model_state[0],
        'velocity': model_state[1],
        'angle': model_state[2],
        'rotation': model_state[3],
    }


def terminal(model_state):
    """ Return true if the state should end the episode. This includes both
        failure terminals (such as when the model isout-of-bounds) and success
        terminals (when the model is in a successful state)
    """
    x, x_dot, theta, theta_dot = model_state
    theta_threshold_radians = 12 * 2 * math.pi / 360
    x_threshold = 2.4
 
    # Terminal occurs when the cart's position is too far to the left or right
    # or the cart's pole has tipped too far.
    done = (x < -x_threshold or
            x > x_threshold or
            theta < -theta_threshold_radians or
            theta > theta_threshold_radians)
    return done

def action(brain_action):
    """ Convert the action from the AI Engine to a format expected by the
        CartPole model.
    """
    return 1 if brain_action['command'] > 0 else 0

def reward(model_state, done):
    """ Return greater values to reward the AI for correct behavior.
    """
    # If the AI has not hit a terminal situation reward it with a score of 1.0
    if not done:
        return 1.0
    return -0.01

