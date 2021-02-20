import asyncio
import inspect
import sys
import os
import logging
import typing
import inspect
from functools import wraps

from ..settings import load_env
from .. import utils
from .. import types
from ..events import HivenParsers, HivenEventHandler
from ..gateway import Connection, HTTP
from ..exception import SessionCreateError, InvalidTokenError
from .cache import ClientCache

__all__ = ['HivenClient']

logger = logging.getLogger(__name__)

load_env()
USER_TOKEN_LEN = utils.convert_value(int, os.getenv("USER_TOKEN_LEN"))
BOT_TOKEN_LEN = utils.convert_value(int, os.getenv("BOT_TOKEN_LEN"))


class HivenClient(HivenEventHandler):
    """ Main Class for connecting to Hiven and interacting with the API. """
    def __init__(self, token: str, *, loop: asyncio.AbstractEventLoop = None, log_ws_output: bool = False):
        self._token = token
        self._connection = Connection(self)
        self._loop = loop
        self._log_ws_output = log_ws_output
        self.storage = ClientCache(token, log_ws_output)

        if token is None or token == "":
            logger.critical(f"[HIVENCLIENT] Empty Token was passed!")
            raise InvalidTokenError("Empty Token was passed!")

        elif len(token) not in (USER_TOKEN_LEN, BOT_TOKEN_LEN):
            logger.critical(f"[HIVENCLIENT] Invalid Token was passed!")
            raise InvalidTokenError("Invalid Token was passed!")

        # Inheriting the HivenEventHandler class that will call and trigger the parsers for events
        super().__init__(HivenParsers(self))

    def __str__(self) -> str:
        return getattr(self, "name")

    def __repr__(self) -> str:
        info = [
            ('open', self.open),
            ('name', getattr(self.user, 'name', None)),
            ('id', getattr(self.user, 'id', None))
        ]
        return '<HivenClient {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def token(self) -> str:
        return self.storage.get('token', None)

    @property
    def log_ws_output(self) -> str:
        return self.storage.get('log_ws_output', None)

    @property
    def http(self) -> HTTP:
        return getattr(self.connection, 'http', None)

    @property
    def connection(self) -> Connection:
        return getattr(self, '_connection', None)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return getattr(self, '_loop', None)

    def run(self,
            *,
            loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
            restart: bool = False) -> None:
        """
        Standard function for establishing a connection to Hiven

        :param loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was
                           created yet
        :param restart: If set to True the Client will restart if an error is encountered!
        """
        try:
            # Overwriting the until now None Event Loop
            self._loop = loop
            self.connection._loop = self._loop
            self.loop.run_until_complete(self.connection.connect(restart))

        except KeyboardInterrupt:
            pass

        except Exception as e:
            utils.log_traceback(
                level='critical',
                msg="[HIVENCLIENT] Traceback:",
                suffix=f"Failed to establish or keep the connection alive: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise SessionCreateError(f"Failed to establish HivenClient session! > {sys.exc_info()[0].__name__}: {e}")

    async def close(self):
        """ Closes the Connection to Hiven and stops the running WebSocket and the Event Processing Loop """
        await self.connection.close()
        logger.debug("[HIVENCLIENT] Closing the connection! The WebSocket will stop shortly!")

    @property
    def open(self) -> bool:
        return getattr(self.connection, 'open', False)

    @property
    def startup_time(self) -> int:
        return getattr(self.connection.ws, 'startup_time', None)

    @property
    def user(self):
        return getattr(self, '_user', None)
