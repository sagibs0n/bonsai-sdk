import time
from random import uniform
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.httpclient import HTTPRequest, HTTPError
from bonsai_ai.exceptions import BonsaiServerError, RetryTimeoutError
from bonsai_ai.logger import Logger


_CONNECT_TIMEOUT_SECS = 60

log = Logger()


class SimulatorConnection(object):

    def __init__(self, brain, predict):
        """
        Args:
            brain (bonsai_ai.Brain): Bonsai Brain object containing
                configuration for a user's brain
            predict (bool): Boolean representing if we are predicting or
                training
        """
        self._brain = brain
        self._predict = predict
        self._ws = None
        self._retry_timeout_seconds = brain.config.retry_timeout
        self._connection_attempts = 0
        self._base_multiplier_milliseconds = 50
        self._maximum_backoff_seconds = 60
        self._timeout = None
        self._init_reconnect()

    def _init_reconnect(self):
        """
        Initializes two different sets to check against when attempting to
        reconnect the simulator. The first set 'invalid_reconnect_codes'
        consists of a set of websocket close codes that we cannot or do not
        want to reconnect the simulator.

        invalid_reconnect_codes:
            1001 - Brain has finished training

        The second set 'invalid_reconnect_reasons' is a set of strings that we
        are forced to compare against to determine if the simulator should
        attempt to reconnect. We understand that this is very fragile but with
        the current state of the system, we have no choice but to go with this
        method. In the future we hope that the entire set of invalid reconnect
        reasons can be mapped to a set of close codes that allow us to safely
        say we should not attempt to reconnect the simulator
        """
        self._invalid_reconnect_codes = {1001}
        self._invalid_reconnect_reasons = {
            'Brain {}/{}/{} has already finished training'.format(
                self._brain.config.username,
                self._brain.name,
                self._brain.version
            ),
            'Brain {}/{} does not exist'.format(
                self._brain.config.username,
                self._brain.name
            ),
            'BRAIN {}/{}/{} does not exist'.format(
                self._brain.config.username,
                self._brain.name,
                self._brain.version
            ),
            'No Brain version exists for Brain {}/{}. '
            ' Did you start training before connecting'
            ' simulator?'.format(
                self._brain.config.username,
                self._brain.name
            ),
            'Cannot predict; currently training'
        }

    @property
    def client(self):
        """
        Returns an instance of tornado.websocket.WebSocketClientConnection

        If the client is not connected it returns None
        """
        return self._ws

    @gen.coroutine
    def connect(self):
        self._connection_attempts += 1

        if self._connection_attempts > 1:
            self._handle_reconnect()

        try:
            if self._predict is True:
                url = self._brain._prediction_url()
            else:
                url = self._brain._simulation_url()

            log.info('trying to connect: {}'.format(url))
            req = HTTPRequest(
                url,
                connect_timeout=_CONNECT_TIMEOUT_SECS,
                request_timeout=_CONNECT_TIMEOUT_SECS)
            req.headers['Authorization'] = self._brain.config.accesskey
            req.headers['User-Agent'] = self._brain._user_info

            self._ws = yield websocket_connect(req)
        except Exception as e:
            raise gen.Return(repr(e))
        else:
            self._timeout = None
            self._connection_attempts = 0
            raise gen.Return(None)

    def _handle_reconnect(self):
        if self._timeout and time.time() > self._timeout:
            raise RetryTimeoutError('Simulator Reconnect Time Exceeded')

        if self._retry_timeout_seconds > 0 and self._timeout is None:
            self._timeout = time.time() + self._retry_timeout_seconds
            log.info(
                'Simulator will timeout in {} seconds if it is not able '
                'to connect to the platform.'.format(
                    self._timeout - time.time()))
        self._backoff()

    def _backoff(self):
        """
        Implements Exponential backoff algorithm with full jitter
        Check the following url for more information
        https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
        """
        power_of_two = 2 ** (self._connection_attempts-1)
        max_sleep = min(
            power_of_two * self._base_multiplier_milliseconds / 1000.0,
            self._maximum_backoff_seconds
        )
        sleep = uniform(0, max_sleep)
        log.info('Connection attempt: {}, backing off for {} seconds'.format(
                 self._connection_attempts, sleep))
        time.sleep(sleep)

    @gen.coroutine
    def close(self):
        """ Close the websocket connection """
        log.info('Closing simulator connection')
        if self._ws is not None:
            yield self._ws.close()
            self._ws = None

    def handle_disconnect(self, message=None):
        if message:
            log.info('Error while connecting to websocket: {}'.format(message))

        if self._ws:
            log.info(
                'ws_close_code: {}, ws_close_reason: {}.'.format(
                    self._ws.close_code, self._ws.close_reason))

            if (self._ws.close_code in self._invalid_reconnect_codes or
                    self._ws.close_reason in self._invalid_reconnect_reasons or
                    not self._retry_timeout_seconds):
                raise BonsaiServerError(
                    'Websocket connection closed. Code: {}, Reason: {}'.format(
                        self._ws.close_code, self._ws.close_reason))

        self.close()
