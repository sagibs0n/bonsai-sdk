# Copyright (C) 2018 Bonsai, Inc.

# tornado
from tornado import gen
from tornado.websocket import WebSocketClosedError, StreamClosedError

# protobuf
from google.protobuf.json_format import MessageToJson

# inkling
from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai.proto.generator_simulator_api_pb2 import SimulatorToServer

# bonsai
from bonsai_ai.common.proto_to_state import dict_for_message
from bonsai_ai.event import EpisodeStartEvent, SimulateEvent, \
    EpisodeFinishEvent, FinishedEvent, UnknownEvent
from bonsai_ai.exceptions import SimulateError, EpisodeStartError, \
    BonsaiServerError, EpisodeFinishError
from bonsai_ai.inkling_factory import InklingMessageFactory
from bonsai_ai.logger import Logger
from bonsai_ai.simulator_connection import SimulatorConnection


log = Logger()


class Simulator_WS(object):
    class SimStep(object):
        """
        Internal class used for keeping track of batch-processed
        round trips through the simulator. Packed into a protobuf
        message at the end and sent over the wire.

        """
        def __init__(self):
            self.prediction = None
            self.state = None
            self.reward = 0.0
            self.terminal = False

    def __init__(self, brain, sim, simulator_name):
        self.brain = brain
        self.name = simulator_name
        self._sim = sim
        self._reset_simulator_ws()
        self._sim_connection = SimulatorConnection(brain, sim.predict)

        # protobuf discriptor cache
        self._inkling = InklingMessageFactory()

        self._dispatch_send = {
            ServerToSimulator.UNKNOWN:
                '_send_registration',
            ServerToSimulator.ACKNOWLEDGE_REGISTER:
                '_send_initial_state' if self._sim.predict else '_send_ready',
            ServerToSimulator.SET_PROPERTIES:
                '_unsupported' if self._sim.predict else '_send_ready',
            ServerToSimulator.START:
                '_unsupported' if self._sim.predict else '_send_initial_state',
            ServerToSimulator.PREDICTION:
                '_send_state',
            ServerToSimulator.RESET:
                '_unsupported' if self._sim.predict else '_send_ready',
            ServerToSimulator.STOP:
                '_unsupported' if self._sim.predict else '_send_ready',
        }

        self._dispatch_recv = {
            ServerToSimulator.ACKNOWLEDGE_REGISTER:
                '_on_acknowledge_register',
            ServerToSimulator.SET_PROPERTIES:
                '_on_set_properties',
            ServerToSimulator.START:
                '_on_start',
            ServerToSimulator.PREDICTION:
                '_on_prediction',
            ServerToSimulator.RESET:
                '_on_reset',
            ServerToSimulator.STOP:
                '_on_stop',
            ServerToSimulator.FINISHED:
                '_on_finished'
        }

    def _reset_simulator_ws(self):
        """ Reset state of simulator_ws"""
        log.simulator_ws('Resetting simulator_ws')
        self.objective_name = None
        self._prev_message_type = ServerToSimulator.UNKNOWN

        # acknowledge_register
        # schemas are of type DescriptorProto
        self._properties_schema = None
        self._output_schema = None
        self._prediction_schema = None
        self._sim_id = -1

        # set_properties
        self._init_properties = {}
        self._initial_state = None

        # current batch of simulation steps
        self._sim_steps = []
        self._step_iter = None
        self._prev_step_terminal = [False]
        self._prev_step_finish = False

        # Caching actions for predictor
        self._predictor_action = None

    def _new_state_message(self):
        """
        Generate an InklingMessage for holding simulator state
        :return: state message
        """
        return self._inkling.new_message_from_proto(self._output_schema)

    def _send_registration(self, to_server):
        log.simulator_ws('Sending Registration')
        to_server.message_type = SimulatorToServer.REGISTER
        to_server.register_data.simulator_name = self.name

    def _send_ready(self, to_server):
        log.simulator_ws('Sending Ready')
        to_server.message_type = SimulatorToServer.READY
        to_server.sim_id = self._sim_id

    def _send_initial_state(self, to_server):
        log.simulator_ws('Sending initial State')
        to_server.message_type = SimulatorToServer.STATE
        to_server.sim_id = self._sim_id
        state = to_server.state_data.add()

        state.state = self._initial_state.SerializeToString()
        state.reward = 0.0
        state.terminal = False
        self._prev_step_terminal[0] = state.terminal
        # state.action_taken = #... # no-op for init state

    def _send_state(self, to_server):
        log.simulator_ws('Sending State')
        to_server.message_type = SimulatorToServer.STATE
        to_server.sim_id = self._sim_id
        for step in self._sim_steps:
            if step.state:
                state = to_server.state_data.add()
                state.state = step.state.SerializeToString()
                state.reward = step.reward
                state.terminal = step.terminal
                log.action(self._inkling.message_for_dynamic_message(
                    step.prediction, self._prediction_schema))
                state.action_taken = step.prediction
            else:
                log.simulator("WARNING: Missing step in send_state")
        self._sim_steps = []
        self._step_iter = None

    def _unsupported(self, to_server):
        descriptor = ServerToSimulator.MessageType.DESCRIPTOR
        raise BonsaiServerError(
            "Unexpected Message during {}: {}".format(
                "prediction" if self._sim.predict else "training",
                descriptor.values_by_number[self._prev_message_type].name))

    def _on_acknowledge_register(self, from_server):
        log.simulator_ws('Acknowledging Registration')
        data = from_server.acknowledge_register_data
        self._properties_schema = data.properties_schema
        self._output_schema = data.output_schema
        self._prediction_schema = data.prediction_schema
        if self._sim.writer is not None:
            self._configure_writer()
        self._sim_id = data.sim_id
        log.info("Starting {} ID: <{}>".format(
            "Prediction" if self._sim.predict else "Training",
            self._sim_id))

    def _on_set_properties(self, from_server):
        log.simulator_ws('Setting properties')
        data = from_server.set_properties_data
        self._prediction_schema = data.prediction_schema
        self.objective_name = data.reward_name
        dynamic_properties = data.dynamic_properties
        properties_message = self._inkling.message_for_dynamic_message(
            dynamic_properties, self._properties_schema)
        self._init_properties = dict_for_message(properties_message)

    def _on_start(self, from_server):
        log.simulator_ws('On Start')

    def _on_prediction(self, from_server):
        log.simulator_ws('On Prediction')
        for p_data in from_server.prediction_data:
            step = self.SimStep()
            step.prediction = p_data.dynamic_prediction
            self._sim_steps.append(step)

            # Convert server msg to action dict and saves it for predictor
            self._cache_action_for_predictor(step.prediction)
        self._step_iter = iter(self._sim_steps)

    def _on_reset(self, from_server):
        log.simulator_ws('On Reset')

    def _on_stop(self, from_server):
        log.simulator_ws('On Stop')
        # fire the finished message if the previous step wasn't terminal
        # as it will already have been called
        # if not self._prev_step_terminal:
        #     self._sim._on_episode_finish()

    def _on_finished(self, from_server):
        log.simulator_ws('On Finished')

    def _dump_message(self, message, fname):
        '''Helper function for dumping protobuf message contents'''
        with open(fname, 'wb') as f:
            f.write(message.SerializeToString())

    def _on_send(self, to_server):
        ''' message handler for sending messages to the server '''
        method_name = self._dispatch_send.get(
            self._prev_message_type, 'default')
        method = getattr(self, method_name,
                         lambda x: log.simulator("Finished"))
        method(to_server)

    def _on_recv(self, from_server):
        ''' message handler for server messages '''
        def _raise(msg):
            raise BonsaiServerError(
                "Received unknown message ({}) from server".format(
                    msg.message_type))

        method_name = self._dispatch_recv.get(
            from_server.message_type, 'default')
        method = getattr(self, method_name, _raise)
        method(from_server)
        self._prev_message_type = from_server.message_type

    def _cache_action_for_predictor(self, prediction):
        """ Converts a server prediction into an action dictionary and saves it
            for the predictor class """
        action_message = self._inkling.message_for_dynamic_message(
            prediction, self._prediction_schema)
        self._predictor_action = dict_for_message(action_message)

    def _configure_writer(self):
        self._sim.writer.enable_keys(
            self._fields_for_schema(self._properties_schema), 'config')
        self._sim.writer.enable_keys(
            self._fields_for_schema(self._prediction_schema), 'action')
        self._sim.writer.enable_keys(
            self._fields_for_schema(self._output_schema), 'state')
        self._sim.writer.enable_keys([
            'reward',
            'terminal',
            'time',
            'simulator',
            'predict',
            'sim_id'
        ])
        self._sim.writer.enable_keys([
            'episode_reward',
            'episode_count',
            'episode_rate',
            'iteration_count',
            'iteration_rate'
        ], 'statistics')

    def _fields_for_schema(self, schema):
        msg = self._inkling.new_message_from_proto(schema)
        return [f.name for f in msg.DESCRIPTOR.fields]

    @gen.coroutine
    def _ws_send_recv(self):
        to_server = SimulatorToServer()
        self._on_send(to_server)
        log.pb("to_server: {}".format(MessageToJson(to_server)))

        if (to_server.message_type):
            out_bytes = to_server.SerializeToString()
            try:
                yield self._sim_connection.client.write_message(
                    out_bytes, binary=True)
            except (StreamClosedError, WebSocketClosedError) as e:
                self._sim_connection.handle_disconnect()
                self._reset_simulator_ws()
                return

        # read response from server
        in_bytes = yield self._sim_connection.client.read_message()
        if in_bytes is None:
            self._sim_connection.handle_disconnect()
            self._reset_simulator_ws()
            return

        from_server = ServerToSimulator()
        from_server.ParseFromString(in_bytes)
        log.pb("from_server: {}".format(MessageToJson(from_server)))
        self._on_recv(from_server)

    def _process_sim_step(self):
        try:
            event = None
            step = next(self._step_iter)
            step.state = self._new_state_message()
            if self._prev_step_finish:
                event = EpisodeStartEvent(self._init_properties, step.state)
                self._prev_step_finish = False
            else:
                action_message = self._inkling.message_for_dynamic_message(
                    step.prediction, self._prediction_schema)
                action = dict_for_message(action_message)
                event = SimulateEvent(action, step, self._prev_step_terminal)
            return event
        except StopIteration:
            return None

    @gen.coroutine
    def get_next_event(self):
        """ Update the internal event machine and return the next
        event for processing"""
        # Grab a web socket connection if needed
        if self._sim_connection.client is None:
            message = yield self._sim_connection.connect()
            # If the connection failed, report
            if message is not None:
                self._sim_connection.handle_disconnect(message=message)
                self._reset_simulator_ws()
                raise gen.Return(UnknownEvent())

        if self._prev_message_type == ServerToSimulator.PREDICTION:
            if self._prev_step_terminal[0]:
                self._prev_step_terminal[0] = False
                self._prev_step_finish = True
                event = EpisodeFinishEvent()
            else:
                event = self._process_sim_step()
            if event is not None:
                raise gen.Return(event)

        yield self._ws_send_recv()

        pmt = self._prev_message_type
        if pmt == ServerToSimulator.ACKNOWLEDGE_REGISTER:
            if self._sim.predict:
                self._initial_state = self._new_state_message()
                event = EpisodeStartEvent(
                    self._init_properties, self._initial_state)
                self._prev_step_finish = False
            else:
                event = UnknownEvent()
        elif (pmt == ServerToSimulator.SET_PROPERTIES or
              pmt == ServerToSimulator.RESET):
            event = UnknownEvent()
        elif pmt == ServerToSimulator.STOP:
            if self._prev_step_finish:
                event = UnknownEvent()
                self._prev_step_finish = False
            else:
                event = EpisodeFinishEvent()
        elif pmt == ServerToSimulator.START:
            self._initial_state = self._new_state_message()
            event = EpisodeStartEvent(
                self._init_properties, self._initial_state)
            self._prev_step_finish = False
        elif pmt == ServerToSimulator.PREDICTION:
            event = self._process_sim_step()
        elif pmt == ServerToSimulator.FINISHED:
            event = FinishedEvent()
        else:
            event = UnknownEvent()

        raise gen.Return(event)

    @gen.coroutine
    def run(self):
        """ Run loop called from Simulator. Encapsulates one round trip
        to the backend, which might include a simulation loop.
        """

        event = yield self.get_next_event()

        if isinstance(event, EpisodeStartEvent):
            log.event("Episode Start")
            try:
                state = self._sim._on_episode_start(event.initial_properties)
            except Exception as e:
                raise EpisodeStartError(e)

            event.initial_state = state
            log.simulator("initial state: {}".format(event.initial_state))
            log.simulator_ws('\tES')
        elif isinstance(event, SimulateEvent):
            log.event("Simulate")
            try:
                log.simulator("action: {}".format(event.action))
                event.state, event.reward, event.terminal = \
                    self._sim._on_simulate(event.action)
            except Exception as e:
                raise SimulateError(e)

            log.simulator_ws('\tT' if event.terminal else '\tS')
            log.simulator("state: {}".format(event.state))
        elif isinstance(event, EpisodeFinishEvent):
            log.event("Episode Finish")
            try:
                self._sim._on_episode_finish()
            except Exception as e:
                raise EpisodeFinishError(e)
            log.simulator_ws('\tF')
        elif isinstance(event, FinishedEvent):
            log.event("Finished")
            self._sim_connection.close()
            raise gen.Return(False)
        elif isinstance(event, UnknownEvent):
            log.event("No Operation")

        raise gen.Return(True)
