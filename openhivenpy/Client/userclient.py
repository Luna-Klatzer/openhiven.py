import asyncio
from typing import Optional

from .hivenclient import HivenClient

class UserClient(HivenClient):
    """`openhivenpy.Client.UserClient`
    
    UserClient
    ~~~~~~~~~~
    
    Class for the specific use of a user client on Hiven
    
    The class inherits all the attributes from HivenClient and will initialize with it
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions. Creates a new one on default!
    
    """
    def __init__(self, token: str, heartbeat=30000, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop()):

        self._CLIENT_TYPE = "HivenClient.UserClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, event_loop=event_loop)

    def __repr__(self) -> str:
        return str(self._CLIENT_TYPE)

    def __str__(self) -> str:
        return str(self._CLIENT_TYPE)

        