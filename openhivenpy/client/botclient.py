import asyncio
import logging
import os
import typing

from .hivenclient import HivenClient

__all__ = ['BotClient']

logger = logging.getLogger(__name__)


class BotClient(HivenClient):
    """
    Class for the specific use of a bot Application on Hiven
    """
    def __init__(
                self, 
                token: str, 
                *,
                heartbeat: typing.Optional[int] = None,
                loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                close_timeout: typing.Optional[int] = None,
                receive_timeout: typing.Optional[int] = None,
                log_ws_output: typing.Optional[bool] = False,
                **kwargs):
        """
        :param token: Authorization Token for Hiven
        :param heartbeat: Intervals in which the bot will send heartbeats to the Websocket.
                          Defaults to the pre-set environment heartbeat (30000)
        :param loop: Event loop that will be used to execute all async functions.
                           Will use 'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one
                           was created yet.
        :param close_timeout: Seconds after the websocket will timeout after the end handshake didn't complete
                              successfully. Defaults to the pre-set environment close_timeout (40)
        :param receive_timeout: Timeout for receiving a message from the Hiven Server. Defaults to
        :param log_ws_output: Will additionally to normal debug information also log the ws responses
        """
        self._CLIENT_TYPE = "bot"
        self._bot = True
        super().__init__(
            token=token,
            loop=loop,
            log_ws_output=log_ws_output
        )
        if heartbeat:
            self.connection._heartbeat = heartbeat
        if close_timeout:
            self.connection._close_timeout = close_timeout
        if receive_timeout:
            self.connection._receive_timeout = receive_timeout

    def __repr__(self) -> str:
        info = [
            ('type',  getattr(self, '_CLIENT_TYPE', None)),
            ('open', getattr(self, 'open')),
            ('bot', getattr(self, 'bot', True)),
            ('name', getattr(self.user, 'name')),
            ('id', getattr(self.user, 'id'))
        ]
        return '<BotClient {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def client_type(self) -> str:
        return getattr(self, '_CLIENT_TYPE', None)
