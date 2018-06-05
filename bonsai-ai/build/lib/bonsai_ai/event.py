from bonsai_ai.common.state_to_proto import convert_state_to_proto
from bonsai_ai.common.proto_to_state import dict_for_message


class Event(object):
    pass


class EpisodeStartEvent(Event):
    """
    This event is generated at the start of a training episode.
    It is triggered either by a terminal condition in the simulator
    or by the platform itself.

    Attributes:
        initial_properties: Configuration properties for the simulator.
        initial_state:      Assign the state resulting from a model reset.

    Example Usage:
        event = get_next_event()
        if isinstance(event, EpisodeStartEvent):
            state = episode_start(event.initial_properties)
            if state is not None:
                event.initial_state = state
    """
    def __init__(self, initial_properties, initial_state):
        self._initial_properties = initial_properties
        self._initial_state = initial_state

    @property
    def initial_properties(self):
        return self._initial_properties

    @property
    def initial_state(self):
        return dict_for_message(self._initial_state)

    @initial_state.setter
    def initial_state(self, state):
        if state is not None:
            convert_state_to_proto(self._initial_state, state)


class SimulateEvent(Event):
    """ This event is generated when an action (prediction) is ready
    to be fed into the simulator.

    Attributes:
        action:   Next action (prediction) in the queue.
        state:    Assign the resulting state after updating the model.
        reward:   The reward calculated from the updated.
        terminal: Whether the updated state is terminal
    """
    def __init__(self, action, sim_step, prev_step_term):
        self._action = action
        self._sim_step = sim_step
        self._prev_step_term = prev_step_term

    @property
    def action(self):
        return self._action

    @property
    def state(self):
        return dict_for_message(self._sim_step.state)

    @state.setter
    def state(self, state):
        if state is not None:
            convert_state_to_proto(self._sim_step.state, state)

    @property
    def reward(self):
        return self._sim_step.reward

    @reward.setter
    def reward(self, reward):
        self._sim_step.reward = reward

    @property
    def terminal(self):
        return self._sim_step.terminal

    @terminal.setter
    def terminal(self, terminal):
        self._prev_step_term[0] = self._sim_step.terminal = terminal


class EpisodeFinishEvent(Event):
    """ Indicates that an episode is ending. Provides an opportunity
    to do any end of episode book keeping (reset counters, etc).
    """
    pass


class FinishedEvent(Event):
    """ The Bonsai platform has terminated training."""
    pass


class UnknownEvent(Event):
    """ Catch all event for other internal states. Usually results in a NOOP
    in user code"""
    pass
