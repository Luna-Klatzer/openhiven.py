import asyncio
import inspect
import sys
import os
import logging
import typing
from functools import wraps

from ..settings import load_env
from .. import utils
from .. import types
from ..events import Parsers
from ..gateway import Connection, HTTP
from ..exception import SessionCreateError, ExpectedAsyncFunction

__all__ = ['HivenClient']

logger = logging.getLogger(__name__)


class HivenClient:
    """
    Main Class for connecting to Hiven and interacting with the API.
    """
    def __init__(self, token: str, *, loop: asyncio.AbstractEventLoop = None, log_ws_output: bool = False):
        self._token = token
        self._connection = Connection(self)
        self._loop = loop
        self._log_ws_output = log_ws_output
        # Creating an instance of the class that will call and trigger the event parsers
        self.parsers = Parsers(self)

    def __str__(self) -> str:
        return getattr(self, "name")

    @property
    def token(self) -> str:
        return getattr(self, '_token', None)

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
        finally:
            self.connection._connection_status = "CLOSED"

    async def close(self):
        """ Closes the Connection to Hiven and stops the running WebSocket and the Event Processing Loop """
        await self.connection.close()

    @property
    def open(self) -> bool:
        return getattr(self.connection, 'open', False)

    @property
    def startup_time(self) -> int:
        return getattr(self.connection.ws, 'startup_time', None)

    @property
    def user(self):
        return getattr(self, '_user', None)

    def event(self, func: typing.Union[typing.Callable, typing.Coroutine] = None):
        """
        Decorator used for registering Client Events

        :param func: Function that should be wrapped.
        """

        def decorator(func_: typing.Union[typing.Callable, typing.Coroutine]):
            if not inspect.iscoroutinefunction(func_):
                raise ExpectedAsyncFunction("The decorated event_listener requires to be async!")

            @wraps(func_)
            async def wrapper(*args, **kwargs):
                return await func_(*args, **kwargs)

            setattr(self, func_.__name__, wrapper)  # Adding the function to the object

            logger.debug(f"[EVENT-HANDLER] >> Event {func_.__name__} registered")

            return func_  # func can still be used normally

        if func is None:
            return decorator
        else:
            return decorator(func)

