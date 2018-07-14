def state(observation):
    return {'position': observation[0],
            'velocity': observation[1],
            'angle':    observation[2],
            'rotation': observation[3]}


def action(event):
    return event.action['command']


# included for completeness w.r.t. the "STAR" pattern
# for more information, see Bonsai documentation
def terminal(val):
    return bool(val)


# included for completeness w.r.t. the "STAR" pattern
# for more information, see Bonsai documentation
def reward(val):
    return float(val)


def params(event):
    return event.initial_properties
