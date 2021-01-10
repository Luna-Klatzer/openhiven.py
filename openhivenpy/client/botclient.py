import asyncio
import logging
import os
from typing import Optional

from openhivenpy.settings import load_env
from .hivenclient import HivenClient

__all__ = 'BotClient'

logger = logging.getLogger(__name__)


class BotClient(HivenClient):
    """`openhivenpy.BotClient`
    
    BotClient
    ~~~~~~~~~
    
    Class for the specific use of a bot client on Hiven
    
    The class inherits all the attributes from HivenClient and will initialize with it
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven.
                    Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions.
                                                        Creates a new one on default!
    
    log_ws_output: `bool` - Will additionally to normal debug information also log the ws responses
    
    """
    def __init__(
                self, 
                token: str, 
                *,
                event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop(), 
                **kwargs):

        self._CLIENT_TYPE = "bot"
        super().__init__(token=token, 
                         client_type=self._CLIENT_TYPE,
                         event_loop=event_loop, 
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
