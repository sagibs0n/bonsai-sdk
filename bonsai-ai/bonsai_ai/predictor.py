from bonsai_ai import Simulator
from bonsai_ai.logger import Logger
from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator

log = Logger()

_CONNECT_TIMEOUT_SECS = 60


class Predictor(Simulator):
    """
    This class is used to interface with the server to obtain
    predictions for a specific BRAIN.

    The `Predictor` class is closely related to the Inkling file that
    is associated with the BRAIN. The name used to construct `Predictor`
    must match the name of the simulator in the Inkling file.

    Attributes:
        brain:      The BRAIN to connect to.
        name:       The name of this Simulator. Must match simulator
                    in inkling.

    Example Inkling:
        simulator my_simulator(Config)
            action (Action)
            state (State)
        end

    Example Code:

        As a context manager:
            config = bonsai_ai.Config(sys.argv)
            brain = bonsai_ai.Brain(config)
            predictor = Predictor(brain, "my_simulator")

            with predictor:
                action = predictor.get_action(state)

        Without context manager:
            config = bonsai_ai.Config(sys.argv)
            brain = bonsai_ai.Brain(config)
            predictor = Predictor(brain, "my_simulator")

            action = predictor.get_action(state)
            predictor.close()
    """

    def __init__(self, brain, name):
        """
        Constructs the Simulator class.

        Arguments:
            brain: The BRAIN you wish to predict against.
            name:  The Simulator name. Must match the name in Inkling.
        """
        super(Predictor, self).__init__(brain, name)

        self._state = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def predict(self):
        return True

    def episode_start(self, init_properties):
        return self._state

    def simulate(self, action):
        self.action_to_client = action

        return self._state, 0, False

    def get_action(self, state):
        """ Returns an action for a given state """
        if self._impl._prev_message_type == ServerToSimulator.UNKNOWN:
            self.run()

        self._state = state

        self.run()

        return self._impl._predictor_action
