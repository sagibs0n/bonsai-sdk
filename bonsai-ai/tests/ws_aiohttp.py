import json
import sys
from google.protobuf.json_format import Parse

from time import sleep

from bonsai_ai.proto.generator_simulator_api_pb2 import ServerToSimulator
from bonsai_ai.proto.generator_simulator_api_pb2 import SimulatorToServer

from aiohttp import web, WSMsgType, WSCloseCode, EofStream
import weakref
import os
import async_timeout


def count_me(fnc):
    """ decorator to count function calls in a class variable
    """
    def increment(self, *args, **kwargs):
        self._count += 1
        return fnc(self, *args, **kwargs)
    return increment


BRAIN_STATUS = {'versions': [{'version': 3}, {'version': 2}],
                'state': 'Not Started'}

SIMS = {"cartpole_simulator": {"inactive": [], "active": []},
        "random_simulator": {"inactive": [], "active": []}}

USER_STATUS = {'brains': [{'name': "cartpole"}]}


class BonsaiWS:
    _PROTOCOL_FILE = "proto_bin/cartpole_wire.json"
    _PREDICT = False
    _FLAKY = False
    _UNAUTHORIZED = False
    _SLOW = False
    _EOFSTREAM = False
    _ERROR_MSG = False
    _PONG = False
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

    def __init__(self, protocol):
        with open(protocol, 'r') as f:
            j = f.read()
            self._message_data = json.loads(j)

    def reset_flags(self):
        self._UNAUTHORIZED = False
        self._FLAKY = False
        self._PREDICT = False
        self._EOFSTREAM = False
        self._ERROR_MSG = False
        self._PONG = False

    async def load_cartpole(self, request):
        p_file = "{}/proto_bin/cartpole_wire.json".format(
                os.path.dirname(__file__))
        with open(p_file, 'r') as f:
            j = f.read()
            self._message_data = json.loads(j)

    async def load_luminance(self, request):
        p_file = "{}/proto_bin/luminance_wire.json".format(
                os.path.dirname(__file__))
        with open(p_file, 'r') as f:
            j = f.read()
            self._message_data = json.loads(j)

    async def reset(self, request):
        self._count = 0
        return web.Response()

    async def auth_train(self, request):
        self.reset_flags()
        self._UNAUTHORIZED = True
        return await self.handle_msg(request)

    async def flaky_train(self, request):
        self.reset_flags()
        self._FLAKY = True
        return await self.handle_msg(request)

    async def flaky_predict(self, request):
        self.reset_flags()
        self._FLAKY = True
        self._PREDICT = True
        return await self.handle_msg(request)

    async def train(self, request):
        self.reset_flags()
        return await self.handle_msg(request)

    async def predict(self, request):
        self.reset_flags()
        self._PREDICT = True
        return await self.handle_msg(request)

    async def eofstream(self, request):
        self.reset_flags()
        self._EOFSTREAM = True
        return await self.handle_msg(request)

    async def error_msg(self, request):
        self.reset_flags()
        self._ERROR_MSG = True
        return await self.handle_msg(request)
  
    async def handle_pong(self, request):
        self.reset_flags()
        self._PONG = True
        return await self.handle_msg(request)

    @count_me
    async def handle_msg(self, request):
        self._prev = ServerToSimulator.UNKNOWN
        if self._UNAUTHORIZED:
            return web.Response(status=401, text="Unauthorized")

        if self._FLAKY and \
           self._count > self._fail_point and \
           self._count < self._fail_point + self._fail_duration:
            return web.Response(status=503, text="Service Unavailable")

        ws = web.WebSocketResponse()
        await ws.prepare(request)
        ws.force_close()

        if self._PONG:
            if os.path.exists('pong.json'):
                os.remove('pong.json')
            with async_timeout.timeout(1, loop=ws._loop):
                msg = await ws._reader.read()
            if msg.type == WSMsgType.PONG:
                pong_json = {'PONG': 1}
                with open('pong.json', 'w') as outfile:
                    json.dump(pong_json, outfile)
            await ws.close()
            return ws

        request.app['websockets'].add(ws)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.CLOSE:
                    await ws.close()
                else:
                    self._count += 1
                    from_sim = SimulatorToServer()
                    from_sim.ParseFromString(msg.data)
                    self._validate_message(from_sim)
                    sim_name = from_sim.register_data.simulator_name
                    mtype = self._dispatch_mtype(from_sim.message_type)

                    if self._FLAKY and \
                       self._count > self._fail_point and \
                       self._count < self._fail_point + self._fail_duration:
                        await ws.close(code=1008, message=b'')
                        return ws
                    elif BRAIN_STATUS['state'] == "Stopped":
                        await ws.close(
                            # code 1001 means: brain has finished training
                            code=1001,
                            message=b"Brain no longer training"
                        )
                        return ws
                    elif (from_sim.message_type == SimulatorToServer.REGISTER and
                          sim_name not in SIMS.keys()):
                        msg = "Simulator {} does not exist.".format(sim_name)
                        await ws.close(
                            # code 4043 means: simulator does not exist
                            code=4043, message=bytes(msg, 'utf-8'))
                        return ws

                    if self._EOFSTREAM:
                        await ws.send_bytes(EofStream())
                    elif self._ERROR_MSG:
                        await ws.send_bytes('foo')
                    else:
                        # dict->json->Message->binary
                        msg_dict = self._message_data[mtype]
                        json_msg = json.dumps(msg_dict)
                        msg = ServerToSimulator()
                        Parse(json_msg, msg)
                        await ws.send_bytes(msg.SerializeToString())

                    self._prev = mtype
        finally:
            request.app['websockets'].discard(ws)

        await ws.close()
        return ws

    async def on_shutdown(self, app):
        for ws in set(app['websockets']):
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')


def open_bonsai_ws(protocol):
    bonsai_ws = BonsaiWS(protocol)
    bonsai_ws.reset_flags()
    app = web.Application()
    app['websockets'] = weakref.WeakSet()
    app.on_shutdown.append(bonsai_ws.on_shutdown)
    # TODO(oren.leiman): add the BRAIN request handler
    app.router.add_get('/v1/alice/cartpole/sims/ws',
                       bonsai_ws.train)
    app.router.add_get('/v1/alice/cartpole/4/predictions/ws',
                       bonsai_ws.predict)
    app.router.add_get('/v1/flake/cartpole/sims/ws',
                       bonsai_ws.flaky_train)
    app.router.add_get('/v1/needsauth/cartpole/sims/ws',
                       bonsai_ws.auth_train)
    app.router.add_get('/v1/flake/cartpole/4/predictions/ws',
                       bonsai_ws.flaky_predict)
    app.router.add_get('/v1/eofstream/cartpole/sims/ws',
                       bonsai_ws.eofstream)
    app.router.add_get('/v1/error_msg/cartpole/sims/ws',
                       bonsai_ws.error_msg)
    app.router.add_get('/v1/pong/cartpole/sims/ws',
                       bonsai_ws.handle_pong)
    app.router.add_patch('/reset',
                         bonsai_ws.reset)
    app.router.add_patch('/luminance',
                         bonsai_ws.load_luminance)
    app.router.add_patch('/cartpole',
                         bonsai_ws.load_cartpole)
    # ])
    return app


def close_bonsai_ws(app):
    pass


def set_predict_mode(predict):
    pass


def set_flaky_mode(flaky):
    pass


def set_unauthorized_mode(unauthorized):
    """ Returns 401 error on get requests when set to True """
    BonsaiWS._UNAUTHORIZED = unauthorized


def set_slow_mode(slow):
    BonsaiWS._SLOW = slow


def set_fail_duration(duration):
    duration = int(duration)
    if duration < 0:
        raise ValueError(
            'Fail duration cannot be negative. '
            'If you wish to turn off flakiness, use set_flaky_mode.')
    BonsaiWS._fail_duration = duration


def reset_count():
    BonsaiWS._count = 0


if __name__ == '__main__':
    the_app = open_bonsai_ws(sys.argv[1])
    web.run_app(app=the_app, host="127.0.0.1", port=9000)
