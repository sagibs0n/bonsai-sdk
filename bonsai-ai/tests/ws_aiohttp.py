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
from typing import Any, cast


def count_me(fnc):
    """ decorator to count function calls in a class variable
    """
    def increment(self, *args, **kwargs):
        self._count += 1
        return fnc(self, *args, **kwargs)
    return increment


BRAIN_INFO = {
    'versions': [{'url': '/v1/alice/cartpole/1', 'version': 1}],
    'description': 'pole',
    'name': 'cartpole',
    'user': 'alice'
}

BRAIN_STATUS = {
    "concepts": [
        {
            "algorithm": "DQN",
            "concept_name": "Balance",
            "is_estimator": False,
            "name": "Balance",
            "objective_name": "???",
            "state": "In Progress",
            "training_end": "",
            "training_start": "2019-04-02T18:01:40Z"
        }
    ],
    "episode": 0,
    "episode_length": 0,
    "iteration": None,
    "models": 1,
    "name": "safsaf",
    "objective_name": "Balance_objective",
    "objective_score": 0.0,
    "simulator_loaded": None,
    "simulator_manageable": True,
    "simulators": [],
    "state": "In Progress",
    "test_episode": None,
    "test_episode_length": None,
    "test_objective_score": None,
    "training_end": "",
    "training_start": "2019-04-02T18:01:28.220000Z",
    "user": "alice",
    "version": 1,
    "versions": [
        {
            "iterations": None,
            "last_modified": "2019-04-02T18:01:40.872000Z",
            "reward": None,
            "version": 1
        }
    ]
}

SIMS = {"cartpole_simulator": {"inactive": [], "active": []},
        "random_simulator": {"inactive": [], "active": []}}

USER_STATUS = {'brains': [{'name': "cartpole"}]}

START_STOP_RESUME = {
    "brain_url": "/v1/alice/cartpole/1",
    "compiler_version": "2.0.0",
    "manage_simulator": False,
    "name": "cartpole",
    "simulator_connect_url": "/v1/alice/cartpole/sims/ws",
    "simulator_predictions_url": "/v1/admin/b1/latest/predictions/ws",
    "user": "alice",
    "version": "latest"
}

METRICS = {
    "episode": 1,
    "lesson": "balancing",
    "value": 25,
    "iteration": 1354,
    "concept": "balance",
    "time": "2017-11-10T06:37:11.712068096Z"
}

CREATE_PUSH = {
    "description": "",
    "files": [
        "cartpole.ink"
    ],
    "ink_compile": {
        "compiler_version": "2.0.0",
        "errors": [],
        "inkling_version": "2.0",
        "success": True,
        "warnings": []
    },
    "name": "cartpole",
    "url": "/v1/alice/cartpole"
}

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
        return web.Response()

    async def load_luminance(self, request):
        p_file = "{}/proto_bin/luminance_wire.json".format(
            os.path.dirname(__file__))
        with open(p_file, 'r') as f:
            j = f.read()
            self._message_data = json.loads(j)
        return web.Response()

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

    async def start_stop_resume(self, request):
        self.reset_flags()
        return web.json_response(START_STOP_RESUME)

    async def metrics(self, request):
        self.reset_flags()
        return web.json_response(METRICS)

    async def status(self, request):
        self.reset_flags()
        return web.json_response(BRAIN_STATUS)

    async def info(self, request):
        self.reset_flags()
        return web.json_response(BRAIN_INFO)

    async def delete_brain(self, request):
        self.reset_flags()
        return web.json_response({})

    async def sims_info(self, request):
        self.reset_flags()
        return web.json_response(SIMS)
    
    async def create_push(self, request):
        self.reset_flags()
        return web.json_response(CREATE_PUSH)

    async def root(self, request):
        self.reset_flags()
        return web.json_response({})

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
                        # Intentionally send a bad parameter
                        await ws.send_bytes(cast(Any, EofStream()))
                    elif self._ERROR_MSG:
                        # Intentionally send a bad parameter
                        await ws.send_bytes(cast(Any, 'foo'))
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
    app.router.add_get('/', bonsai_ws.root)
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
    app.router.add_get('/v1/alice/cartpole',
                       bonsai_ws.info)
    app.router.add_get('/v1/alice/cartpole/status',
                       bonsai_ws.status)
    app.router.add_get('/v1/alice/cartpole/sims',
                       bonsai_ws.sims_info)
    app.router.add_get('/v1/alice/cartpole/latest/metrics/episode_value',
                       bonsai_ws.metrics)
    app.router.add_get('/v1/alice/cartpole/latest/metrics/test_pass_value',
                       bonsai_ws.metrics)
    app.router.add_get('/v1/alice/cartpole/latest/metrics/iterations',
                       bonsai_ws.metrics)
    app.router.add_put('/v1/alice/cartpole/train',
                       bonsai_ws.start_stop_resume)
    app.router.add_put('/v1/alice/cartpole/stop',
                       bonsai_ws.start_stop_resume)
    app.router.add_put('/v1/alice/cartpole/latest/resume',
                       bonsai_ws.start_stop_resume)
    app.router.add_put('/v1/alice/cartpole',
                       bonsai_ws.create_push)
    app.router.add_post('/v1/alice/brains',
                        bonsai_ws.create_push)
    app.router.add_delete('/v1/alice/cartpole',
                          bonsai_ws.delete_brain)
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
