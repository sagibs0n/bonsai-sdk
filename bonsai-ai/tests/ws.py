# Copyright (C) 2018 Bonsai, Inc.

import json
import sys
from tornado import web, websocket, ioloop
from google.protobuf.json_format import Parse

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai.proto.generator_simulator_api_pb2 import SimulatorToServer


class BrainRequestHandler(web.RequestHandler):
    response = {'versions': [{'version': 2}],
                'state': 'Stopped'}

    def get(self):
        self.write(self.response)


class BonsaiWS(websocket.WebSocketHandler):
    '''
    Dummy handler to stand in for the Bonsai backend during testing.
    It is accessed through the pytest fixture `bonsai_ws`.
    To use it in a pytest unit test, just add `bonsai_ws` to the
    argument list of the target test function, as in:

    def test_some_feature(bonsai_ws):
        assert 1

    Super handy!
    '''
    _PROTOCOL_FILE = "proto_bin/cartpole_wire.json"

    _prev = ServerToSimulator.UNKNOWN
    _dispatch = {
        ServerToSimulator.UNKNOWN: {
            SimulatorToServer.REGISTER: ServerToSimulator.ACKNOWLEDGE_REGISTER
        },
        ServerToSimulator.ACKNOWLEDGE_REGISTER: {
            SimulatorToServer.READY: ServerToSimulator.SET_PROPERTIES,
            SimulatorToServer.STATE: ServerToSimulator.PREDICTION
        },
        ServerToSimulator.SET_PROPERTIES: {
            SimulatorToServer.READY: ServerToSimulator.START
        },
        ServerToSimulator.START: {
            SimulatorToServer.STATE: ServerToSimulator.PREDICTION
        },
        ServerToSimulator.PREDICTION: {
            SimulatorToServer.STATE: ServerToSimulator.STOP
        },
        ServerToSimulator.STOP: {
            SimulatorToServer.READY: ServerToSimulator.RESET,
            SimulatorToServer.STATE: ServerToSimulator.FINISHED
        },
        ServerToSimulator.RESET: {
            SimulatorToServer.READY: ServerToSimulator.SET_PROPERTIES
        }
    }
    _message_data = None

    def _dispatch_mtype(self, incoming):
        return self._dispatch.get(self._prev, {}).get(
            incoming, ServerToSimulator.UNKNOWN)

    def _validate_message(self, msg):
        ''' Add code here to confirm messages have been correctly
        populated in the client'''
        if msg.sim_id == 0 \
           and msg.message_type != SimulatorToServer.REGISTER:
            raise Exception(
                "Sim ID missing from SimulatorToServer message!")

    def open(self):
        ''' When the first client connects, read the message data from
        disk'''
        if self._message_data is not None:
            return
        with open(self._PROTOCOL_FILE, 'r') as f:
            j = f.read()
            self._message_data = json.loads(j)

    def on_message(self, in_bytes):
        from_sim = SimulatorToServer()
        from_sim.ParseFromString(in_bytes)
        self._validate_message(from_sim)
        mtype = self._dispatch_mtype(from_sim.message_type)

        # dict->json->Message->binary
        msg_dict = self._message_data[mtype]
        json_msg = json.dumps(msg_dict)
        msg = ServerToSimulator()
        Parse(json_msg, msg)

        self.write_message(msg.SerializeToString(), binary=True)
        self._prev = mtype

    def on_close(self):
        pass


# These could be probably be defined dynamically, but the fixtures
# `predict_config` and `train_config` both reflect these values.
application = web.Application([
    (r'/v1/alice/cartpole/sims/ws', BonsaiWS),
    (r'/v1/alice/cartpole/4/predictions/ws', BonsaiWS),
    (r'/v1/alice/cartpole/status', BrainRequestHandler),
    (r'/v1/alice/cartpole', BrainRequestHandler)
])


def open_bonsai_ws(protocol):
    BonsaiWS._PROTOCOL_FILE = protocol
    return application.listen(8889)


def close_bonsai_ws():
    loop = ioloop.IOLoop.instance()
    loop.add_callback(loop.stop)
    loop.start()


if __name__ == "__main__":
    try:
        open_bonsai_ws(sys.argv[1])
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        close_bonsai_ws()
