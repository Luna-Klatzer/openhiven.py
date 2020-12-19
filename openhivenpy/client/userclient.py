import asyncio
import logging
import os
from typing import Optional, Union

from .hivenclient import HivenClient
from openhivenpy.settings import load_env
import openhivenpy.types as types
import openhivenpy.utils as utils

__all__ = 'UserClient'

logger = logging.getLogger(__name__)


class UserClient(HivenClient):
    """`openhivenpy.UserClient`
    
    UserClient
    ~~~~~~~~~~
    
    Class for the specific use of a user client on Hiven
    
    The class inherits all the attributes from HivenClient and will initialize with it
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven.
                    Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    event_handler: `openhivenpy.events.EventHandler` - Handler for the events. Can be modified and customized if wanted.
                                                        Creates a new one on Default
    
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

        self._CLIENT_TYPE = "user"
        super().__init__(token=token, 
                         client_type=self._CLIENT_TYPE,
                         event_loop=event_loop, 
                         **kwargs)

    def __repr__(self) -> str:
        return str(self._CLIENT_TYPE)

    def __str__(self) -> str:
        return str(self._CLIENT_TYPE)
        
    async def cancel_friend_request(self, user_id=None, **kwargs) -> Union[bool, None]:
        """`openhivenpy.UserClient.cancel_friend_request()`
 
        Cancels an open friend request if it exists
        
        Returns `True` if successful
        
        Parameter
        ~~~~~~~~
        
        user_id: `int` - Id of the user that sent the friend request
        
        user:
        
        """        
        try:
            if user_id is None:
                user = kwargs.get('user')
                try:
                    user_id = user.id
                except Exception:
                    user_id = None
                if user_id is None:
                    logger.debug("Invalid parameter for cancel_friend_request! Expected user or user_id!")
                    return None
            else:
                resp = await self.http.delete(endpoint=f"/relationships/@me/friend-requests/{user_id}")
                
                if resp.status < 300:
                    return True
                else:
                    return None

        except Exception as e:
            logger.error(f"Failed to cancel the friend request of a user with id {user_id}! Cause of Error {e}")
            return None            

    async def fetch_current_friend_requests(self) -> Union[dict, None]:
        """`openhivenpy.UserClient.fetch_current_friend_requests()`
 
        Fetches all open friend requests on Hiven
        
        Returns a dict with all friend requests
        
        """        
        try:
            resp = await self.http.request(endpoint=f"/relationships/@me/friend-requests")
            if resp.get('success', False):
                data = resp.get('data')
                return {
                    'incoming': list(types.LazyUser(data) for data in data.get('incoming', [])),
                    'outgoing': list(types.LazyUser(data) for data in data.get('outgoing', []))
                }
            else:
                return

        except Exception as e:
            logger.error(f"Failed to fetch the current open friend requests! Cause of Error {e}")
            return None    

    async def block_user(self, user_id=None, **kwargs) -> Union[bool, None]:
        """`openhivenpy.UserClient.block_user()`
        
        Blocks a user
        
        Returns `True` if successful
        
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request!
        
        user_id: `int` - Id of the user that should be blocked
        
        user: `openhivenpy.types.User` - User object that should be blocked

        """
        try:
            if user_id is None:
                user = kwargs.get('user')
                try:
                    user_id = user.id
                except Exception:
                    user_id = None
                if user_id is None:
                    logger.debug("Invalid parameter for block_user! Expected user or user_id!")
                    return None
            else:
                resp = await self.http.put(endpoint=f"/relationships/@me/blocked/{user_id}")
                
                if resp.status < 300:
                    return True
                else:
                    return False

        except Exception as e:
            logger.error(f"Failed to block user with id {user_id}! Cause of error: {e}")

    async def unblock_user(self, user_id=None, **kwargs) -> Union[bool, None]:
        """`openhivenpy.UserClient.unblock_user()`
        
        Unblocks a user if the user is blocked
        
        Returns `True` if successful
        
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request!
        
        user_id: `int` - Id of the user that should be unblocked
        
        user: `openhivenpy.types.User` - User object that should be unblocked
        
        """
        try:
            if user_id is None:
                user = kwargs.get('user')
                try:
                    user_id = user.id
                except Exception:
                    user_id = None
                if user_id is None:
                    logger.debug("Invalid parameter for unblock_user! Expected user or user_id!")
                    return None
            else:
                resp = await self.http.delete(endpoint=f"/relationships/@me/blocked/{user_id}")
                
                if resp.status < 300:
                    return True
                else:
                    return False

        except Exception as e:
            logger.error(f"Failed to unblock a user with id {user_id}! Cause of Error {e}")
            return None

    async def send_friend_request(self, user_id=None, **kwargs) -> Union[types.User, None]:
        """`openhivenpy.UserClient.send_friend_request()`
 
        Sends a friend request to a user
        
        Returns the `User` object if the user exists in the known users
 
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request!
        
        user_id: `int` - Id of the user that should be sent a friend request
        
        user: `openhivenpy.types.User` - User object that should be sent a friend request
        
        """        
        try:
            if user_id is None:
                user = kwargs.get('user')
                try:
                    user_id = user.id
                except Exception:
                    user_id = None
                if user_id is None:
                    logger.debug("Invalid parameter for send_friend_request! Expected user or user_id!")
                    return None
            else:
                resp = await self.http.post(
                                                endpoint=f"/relationships/@me/friend-requests",
                                                json={'user_id': f'{user_id}'})
                
                if resp.status < 300:
                    return utils.get(self.users, id=int(user_id))
                else:
                    return None

        except Exception as e:
            logger.error(f"Failed to send a friend request a user with id {user_id}! Cause of Error {e}")
            return None
