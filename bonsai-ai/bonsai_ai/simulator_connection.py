import time
from random import uniform
from threading import Lock, Thread, Event
from uuid import uuid4
from bonsai_ai.exceptions import BonsaiServerError, RetryTimeoutError
from bonsai_ai.logger import Logger
from .aria_writer import SimConnecting

from aiohttp import ClientSession, WSServerHandshakeError, TCPConnector
import asyncio

from urllib.parse import urlparse

log = Logger()

_PING_PONG_INTERVAL = 15.0


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
        self._session = None
        self._ws = None
        self._retry_timeout_seconds = brain.config.retry_timeout
        self._network_timeout_seconds = brain.config.network_timeout
        self._connection_attempts = 0
        self._base_multiplier_milliseconds = 50
        self._maximum_backoff_seconds = 60
        self._timeout = None
        self.read_timeout_seconds = 240
        self.lock = Lock()
        self._thread_stop = Event()
        self._ioloop = asyncio.get_event_loop()

    @property
    def client(self):
        """
        Returns an instance of tornado.websocket.WebSocketClientConnection

        If the client is not connected it returns None
        """
        return self._ws

    async def connect(self):
        self._connection_attempts += 1

        if self._connection_attempts > 1:
            self._handle_reconnect()

        request_id = str(uuid4())
        try:
            if self._predict is True:
                url = self._brain._prediction_url()
            else:
                url = self._brain._simulation_url()

            if url is None or \
                self._brain.config.accesskey is None or \
                self._brain.config.username is None:
                msg = (
                    'Configuration is invalid. One of the following values URL,'
                    ' ACCESSKEY, or USERNAME is not configured correctly.'
                    ' Current value for URL: {}, ACCESSKEY: {}, USERNAME: {}'
                    ' Please make sure the cli is configured correctly and/or'
                    ' the command line arguments are correct'.format(
                        url, self._brain.config.accesskey, self._brain.config.username))
                self._retry_timeout_seconds = 0
                return msg

            # we only support http proxies, which actually represent
            # most proxies if no scheme is specified, prepend "http://"
            # to make aiohttp happy. if HTTPS is specified, allow websocket
            # connection to blow up on connection
            proxy = self._brain.config.proxy
            if proxy:
                uri = urlparse(proxy)
                if uri.scheme == "":
                    proxy = "http://" + proxy

            log.network('trying to connect: {}'.format(url))
            self._brain._aria_writer.track(SimConnecting(self._predict))
            self._session = ClientSession(
                connector=TCPConnector(force_close=True)
            )

            self._ws = await self._session.ws_connect(
                url,
                timeout=self._network_timeout_seconds,
                heartbeat=_PING_PONG_INTERVAL,
                headers={
                    'Authorization': self._brain.config.accesskey,
                    'User-Agent': self._brain._user_info,
                    'RequestId': request_id
                },
                proxy=proxy
            )
            log.network('Connected to {}'.format(url))
        except WSServerHandshakeError as e:
            log.info("Failed to connect: {}, Request ID: {}".format(
                repr(e), request_id))
            if e.headers is not None:
                try:
                    log.info('Span ID: {}'.format(e.headers['SpanID']))
                except KeyError:
                    pass
            return e
        else:
            self._timeout = None
            self._connection_attempts = 0

            self._thread_stop.clear()
            pong_thread = Thread(target=(self._start_pong_loop))
            pong_thread.daemon = True
            pong_thread.start()
            return None

    def _start_pong_loop(self):
        while not self._thread_stop.is_set():
            self._pong()
            self._thread_stop.wait(_PING_PONG_INTERVAL)

    def _pong(self):
        with self.lock:
            if self._ws:
                log.network('Sending Pong')
                #TODO #10532: Make coroutine when upgrading aiohttp
                self._ws.pong()

    def _handle_reconnect(self):
        log.network('Handling reconnect')

        if self._timeout and time.time() > self._timeout:
            raise RetryTimeoutError('Simulator Reconnect Time Exceeded')

        if self._retry_timeout_seconds > 0 and self._timeout is None:
            self._timeout = time.time() + self._retry_timeout_seconds
            log.info(
                'Simulator will timeout in {} seconds if it is not able '
                'to connect to the platform.'.format(
                    self._timeout - time.time()))
        self._backoff()
        log.network('Reconnect handled')

    def _backoff(self):
        """
        Implements Exponential backoff algorithm with full jitter
        Check the following url for more information
        https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
        """
        power_of_two = 2 ** (self._connection_attempts - 1)
        max_sleep = min(
            power_of_two * self._base_multiplier_milliseconds / 1000.0,
            self._maximum_backoff_seconds
        )
        sleep = uniform(0, max_sleep)
        log.info('Connection attempt: {}, backing off for {} seconds'.format(
            self._connection_attempts, sleep))
        time.sleep(sleep)

    async def close(self):
        """ Close the websocket connection """
        self._thread_stop.set()
        if self._ws:
            if not self._ws.closed:
                with self.lock:
                    log.network('Closing simulator connection')
                    await self._ws.close()
                    log.network('Closed')
            self._ws = None
        else:
            log.network('Websocket was not connected.'
                        'Close() resulted in no operation')
        if self._session:
            await self._session.close()

    def _websocket_should_not_reconnect(self):
        """
        If the websocket's close code is in [4000, 4100),
        that means it was closed for a 'permanent' error
        (e.g., brain is not in the correct state).
        If there is a permanent error, or the retry timeout
        is 0, then don't reconnect.
        :return: True: don't reconnect; False: do reconnect.
        """

        # Code 1001 indicates normal, correct termination.
        if self._ws.close_code == 1001:
            return True

        # So do these codes. We have to work around the older
        # codes and c++ libraries, so we cannot use 1002-2999
        # until the server stops sending them, and the lib
        # will accept them.
        if (self._ws.close_code is not None and
                3000 <= self._ws.close_code <= 3099):
            return True

        # Codes 40xx indicate permanent errors: There is
        # something wrong that will not be fixed by trying
        # again. For example, Brain is not training, or
        # Simulator ticket is incorrect.
        if (self._ws.close_code is not None and
                4000 <= self._ws.close_code <= 4099):
            return True

        if not self._retry_timeout_seconds:
            return True

        return False

    async def handle_disconnect(self, message=None):
        log.network('Handling disconnect')
        self._thread_stop.set()
        if message:
            self._handle_message(message)

        if self._ws:
            if self._websocket_should_not_reconnect():
                raise BonsaiServerError(
                    'Websocket connection closed. Code: {}, Reason: {}'.format(
                        self._ws.close_code, message))
            log.network(
                'ws_close_code: {}, ws_close_reason: {}.'.format(
                    self._ws.close_code, message))

        await self.close()
        log.network('Disconnect handled.')

    def _handle_message(self, message):
        """ Handles error messages returned from initial connection attempt """
        log.network(
            'Handling the following message returned from ws:'
            ' {}'.format(message))
        if isinstance(message, WSServerHandshakeError):
            if message.code == 401:
                raise BonsaiServerError(
                    'Error while connecting to websocket: 401 - Unauthorized. '
                    'Please run \'bonsai configure\' again.')
            if message.code == 404:
                raise BonsaiServerError(
                    'Error while connecting to websocket: 404 - Not Found.')
        if not self._retry_timeout_seconds:
            raise BonsaiServerError(
                'Error while connecting to websocket: {}'.format(message))
        log.network('Error while connecting to websocket: {}'.format(message))
