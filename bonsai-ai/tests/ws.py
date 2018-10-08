# Copyright (C) 2018 Bonsai, Inc.

import json
import logging
import sys
from tornado import web, websocket, ioloop
from google.protobuf.json_format import Parse

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai.proto.generator_simulator_api_pb2 import SimulatorToServer


def count_me(fnc):
    """ decorator to count function calls in a class variable
    """
    def increment(self, *args, **kwargs):
        type(self)._count += 1
        return fnc(self, *args, **kwargs)
    return increment


BRAIN_STATUS = {'versions': [{'version': 3}, {'version': 2}],
                'state': 'Not Started'}

SIMS = {"cartpole_simulator": {"inactive": [], "active": []},
        "random_simulator": {"inactive": [], "active": []}}

USER_STATUS = {'brains': [{'name': "cartpole"}]}


class BrainRequestHandler(web.RequestHandler):

    def get(self):
        uri = self.request.uri
        endpoint = uri.split('/')[-1]
        if (endpoint == 'alice'):
            self.write(USER_STATUS)
        elif (endpoint == 'sims'):
            self.write(SIMS)
        else:
            self.write(BRAIN_STATUS)

    def put(self):
        uri = self.request.uri
        endpoint = uri.split('/')[-1]

        if endpoint == 'train':
            BRAIN_STATUS['state'] = "In Progress"
        elif endpoint == 'stop':
            BRAIN_STATUS['state'] = "Stopped"
        else:
            print("WS.PY: unsupported endpoint: {}".format(uri))

        self.write(BRAIN_STATUS)


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
    _PREDICT = False
    _FLAKY = False
    _fail_point = 10
    _fail_duration = 8

    _prev = ServerToSimulator.UNKNOWN
    _dispatch = {
        ServerToSimulator.UNKNOWN: {
            SimulatorToServer.REGISTER: ServerToSimulator.ACKNOWLEDGE_REGISTER
        },
        ServerToSimulator.ACKNOWLEDGE_REGISTER: {
            SimulatorToServer.READY: ServerToSimulator.SET_PROPERTIES,
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
        },
        ServerToSimulator.RESET: {
            SimulatorToServer.READY: ServerToSimulator.SET_PROPERTIES
        }
    }

    _dispatch_pred = {
        ServerToSimulator.UNKNOWN: {
            SimulatorToServer.REGISTER: ServerToSimulator.ACKNOWLEDGE_REGISTER
        },
        ServerToSimulator.ACKNOWLEDGE_REGISTER: {
            SimulatorToServer.STATE: ServerToSimulator.PREDICTION
        },
        ServerToSimulator.PREDICTION: {
            SimulatorToServer.STATE: ServerToSimulator.PREDICTION
        },
    }

    _message_data = None

    # count connection attemts *AND* incoming messages to
    # control flaky-mode behavior.
    # rejects incoming connections while
    # _fail_point <= _count < _fail_point + _fail_duration

    _count = 0

    def _dispatch_mtype(self, incoming):
        if self._PREDICT:
            return self._dispatch_pred.get(self._prev, {}).get(
                incoming, ServerToSimulator.UNKNOWN)
        else:
            return self._dispatch.get(self._prev, {}).get(
                incoming, ServerToSimulator.UNKNOWN)

    def _validate_message(self, msg):
        ''' Add code here to confirm messages have been correctly
        populated in the client'''
        if msg.sim_id == 0 \
           and msg.message_type != SimulatorToServer.REGISTER:
            raise Exception(
                "Sim ID missing from SimulatorToServer message!")

    @count_me
    def get(self, *args, **kwargs):
        if self._FLAKY and \
           self._count > self._fail_point and \
           self._count < self._fail_point + self._fail_duration:
            self.set_status(503)
            return

        return super(BonsaiWS, self).get(*args, **kwargs)

    def open(self):
        ''' When the first client connects, read the message data from
        disk'''
        if self._message_data is not None:
            return
        with open(self._PROTOCOL_FILE, 'r') as f:
            j = f.read()
            self._message_data = json.loads(j)

    @count_me
    def on_message(self, in_bytes):
        from_sim = SimulatorToServer()
        from_sim.ParseFromString(in_bytes)
        self._validate_message(from_sim)
        sim_name = from_sim.register_data.simulator_name
        mtype = self._dispatch_mtype(from_sim.message_type)

        if self._FLAKY and \
           self._count > self._fail_point and \
           self._count < self._fail_point + self._fail_duration:
            self.close(code=1008, reason="Policy violation.")
            return
        elif BRAIN_STATUS['state'] == "Stopped":
            self.close(code=1001, reason="Brain no longer training")
            return
        elif (from_sim.message_type == SimulatorToServer.REGISTER and
              sim_name not in SIMS.keys()):
            self.close(code=1008,
                       reason="Simulator {} does not exist.".format(sim_name))
            return

        # dict->json->Message->binary
        msg_dict = self._message_data[mtype]
        json_msg = json.dumps(msg_dict)
        msg = ServerToSimulator()
        Parse(json_msg, msg)

        self.write_message(msg.SerializeToString(), binary=True)
        self._prev = mtype

    def on_close(self):
        pass

    def on_ping(self, data):
        print('Received PING: {}'.format(data))

    def on_pong(self, data):
        print("Received PONG: {}".format(data))


# These could be probably be defined dynamically, but the fixtures
# `predict_config` and `train_config` both reflect these values.
application = web.Application([
    (r'/v1/alice/cartpole/sims/ws', BonsaiWS),
    (r'/v1/alice/cartpole/4/predictions/ws', BonsaiWS),
    (r'/v1/alice/cartpole/status', BrainRequestHandler),
    (r'/v1/alice/cartpole/train', BrainRequestHandler),
    (r'/v1/alice/cartpole/stop', BrainRequestHandler),
    (r'/v1/alice/cartpole', BrainRequestHandler),
    (r'/v1/alice/cartpole/sims', BrainRequestHandler),
    (r'/v1/alice', BrainRequestHandler)
])


def open_bonsai_ws(protocol):
    set_predict_mode(False)
    BonsaiWS._PROTOCOL_FILE = protocol
    return application.listen(8889)


def set_predict_mode(predict):
    BonsaiWS._PREDICT = predict


def set_flaky_mode(flaky):
    BonsaiWS._FLAKY = flaky


def set_fail_duration(duration):
    duration = int(duration)
    if duration < 0:
        raise ValueError(
            'Fail duration cannot be negative. '
            'If you wish to turn off flakiness, use set_flaky_mode.')
    BonsaiWS._fail_duration = duration


def reset_count():
    BonsaiWS._count = 0


def close_bonsai_ws():
    loop = ioloop.IOLoop.current()
    loop.add_callback(loop.stop)
    loop.start()


if __name__ == "__main__":
    try:
        open_bonsai_ws(sys.argv[1])
        if sys.argv[2] == "P":
            set_predict_mode(True)
        elif sys.argv[2] == "F":
            set_flaky_mode(True)

        logging.getLogger('tornado.access').disabled = True
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        close_bonsai_ws()
