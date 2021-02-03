import asyncio
import logging
import sys
import traceback
from typing import Optional, Union

from .hivenclient import HivenClient
import openhivenpy.exceptions as errs
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
                                                        Defaults to None!

    close_timeout: `int` -  Seconds after the websocket will timeout after the handshake
                            didn't complete successfully. Defaults to `40`


    log_ws_output: `bool` - Will additionally to normal debug information also log the ws responses
    
    """

    def __init__(
            self,
            token: str,
            *,
            event_loop: Optional[asyncio.AbstractEventLoop] = None,
            **kwargs):

        self._CLIENT_TYPE = "user"
        super().__init__(token=token,
                         client_type=self._CLIENT_TYPE,
                         event_loop=event_loop,
                         **kwargs)

    def __str__(self) -> str:
        return str(getattr(self, 'name'))

    def __repr__(self) -> str:
        info = [
            ('type', self._CLIENT_TYPE),
            ('open', self.open),
            ('name', getattr(self.user, 'name')),
            ('id', getattr(self.user, 'id'))
        ]
        return '<UserClient {}>'.format(' '.join('%s=%s' % t for t in info))

    async def cancel_friend_request(self, user_id: int or float = None, user: types.User = None) -> bool:
        """`openhivenpy.UserClient.cancel_friend_request()`
 
        Cancels an open friend request if it exists
        
        Returns `True` if successful
        
        Parameter
        ~~~~~~~~
        
        user_id: `int` - Id of the user that sent the friend request
        
        user: `openhivenpy.types.User` - User Object
        
        """
        try:
            # Checking if the user was passed and the id can be found
            if user_id is None and user:
                user_id = getattr(user, 'id', None)
                if user_id is None or not isinstance(user, types.User):
                    raise ValueError(f"Expected correct user initialised object! Not {type(user)}")

            # If both are none it will raise an error
            elif user_id is None and user is None:
                raise ValueError("Expected user or user_id that is not None!")

            resp = await self.http.delete(endpoint=f"/relationships/@me/friend-requests/{user_id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix="Failed to cancel the friend request of a user with id {user_id}! \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

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
                return None

        except Exception as e:
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to fetch the current open friend requests; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def block_user(self, user_id: int or float = None, user: types.User = None) -> bool:
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
            # Checking if the user was passed and the id can be found
            if user_id is None and user:
                user_id = getattr(user, 'id', None)
                # TODO! Needs proper check!
                if user_id is None or not isinstance(user, types.User):
                    raise ValueError(f"Expected correct user initialised object! Not {type(user)}")

            # If both are none it will raise an error
            elif user_id is None and user is None:
                raise ValueError("Expected user or user_id that is not None!")

            resp = await self.http.put(endpoint=f"/relationships/@me/blocked/{user_id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to block user with id {user_id}; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def unblock_user(self, user_id: int or float = None, user: types.User = None) -> bool:
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
            # Checking if the user was passed and the id can be found
            if user_id is None and user:
                user_id = getattr(user, 'id', None)
                if user_id is None or not isinstance(user, types.User):
                    raise ValueError(f"Expected correct user initialised object! Not {type(user)}")

            # If both are none it will raise an error
            elif user_id is None and user is None:
                raise ValueError("Expected user or user_id that is not None!")

            resp = await self.http.delete(endpoint=f"/relationships/@me/blocked/{user_id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to unblock a user with id {user_id}; \n"
                                       f" {e}")
            return False

    async def send_friend_request(self, user_id: int or float = None, user: types.User = None) -> bool:
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
            # Checking if the user was passed and the id can be found
            if user_id is None and user:
                user_id = getattr(user, 'id', None)
                if user_id is None or not isinstance(user, types.User):
                    raise ValueError(f"Expected correct user initialised object! Not {type(user)}")

            # If both are none it will raise an error
            elif user_id is None and user is None:
                raise ValueError("Expected user or user_id that is not None!")

            resp = await self.http.post(endpoint=f"/relationships/@me/friend-requests",
                                        json={'user_id': f'{user_id}'})

            if resp.status < 300:
                return utils.get(self.users, id=int(user_id))
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to send a friend request a user with id {user_id}; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False
