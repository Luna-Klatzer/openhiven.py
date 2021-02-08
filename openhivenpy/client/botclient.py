import asyncio
import logging
import os
import typing

from ..events import EventHandler
from .hivenclient import HivenClient
from .. import load_env

__all__ = 'BotClient'

logger = logging.getLogger(__name__)

# Loading the environment variables
load_env()
# Setting the default values to the currently set defaults in the openhivenpy.env file
_default_connection_heartbeat = int(os.getenv("CONNECTION_HEARTBEAT"))
_default_close_timeout = int(os.getenv("CLOSE_TIMEOUT"))


class BotClient(HivenClient):
    """
    Class for the specific use of a bot Application on Hiven
    """
    def __init__(
                self, 
                token: str, 
                *,
                heartbeat: typing.Optional[int] = _default_connection_heartbeat,
                event_loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                event_handler: typing.Optional[EventHandler] = None,
                close_timeout: typing.Optional[int] = _default_close_timeout,
                log_ws_output: typing.Optional[bool] = False,
                **kwargs):
        """
        Object Instance Construction

        :param token: Authorisation Token for Hiven
        :param heartbeat: Intervals in which the bot will send heartbeats to the Websocket.
                          Defaults to the pre-set environment heartbeat (30000)
        :param event_handler: Handler for the events. Creates a new one on Default
        :param event_loop: Event loop that will be used to execute all async functions.
                           Will use 'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one
                           was created yet.
        :param close_timeout: Seconds after the websocket will timeout after the end handshake didn't complete
                              successfully. Defaults to the pre-set environment close_timeout (40)
        :param log_ws_output: Will additionally to normal debug information also log the ws responses
        """
        self._CLIENT_TYPE = "bot"
        super().__init__(token=token, 
                         client_type=self._CLIENT_TYPE,
                         event_loop=event_loop,
                         heartbeat=heartbeat,
                         event_handler=event_handler,
                         close_timeout=close_timeout,
                         log_ws_output=log_ws_output,
                         **kwargs)

    def __str__(self) -> str:
        return str(getattr(self, "name"))

    def __repr__(self) -> str:
        info = [
            ('type', self._CLIENT_TYPE),
            ('open', self.open),
            ('name', getattr(self.user, 'name')),
            ('id', getattr(self.user, 'id'))
        ]
        return '<BotClient {}>'.format(' '.join('%s=%s' % t for t in info))
