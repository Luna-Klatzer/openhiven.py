import asyncio
import logging
import os
import sys
import typing

from ..events import EventHandler
from .hivenclient import HivenClient
from .. import load_env
from ..exceptions import exception as errs
import openhivenpy.types as types
import openhivenpy.utils as utils

__all__ = 'UserClient'

from ..types import entity

logger = logging.getLogger(__name__)

# Loading the environment variables
load_env()
# Setting the default values to the currently set defaults in the openhivenpy.env file
_default_connection_heartbeat = int(os.getenv("CONNECTION_HEARTBEAT"))
_default_close_timeout = int(os.getenv("CLOSE_TIMEOUT"))


class UserClient(HivenClient):
    """
    Class for the specific use of a user account on Hiven
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
        :param event_loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was
                           created yet
        :param close_timeout: Seconds after the websocket will timeout after the end handshake didn't complete
                              successfully. Defaults to the pre-set environment close_timeout (40)
        :param log_ws_output: Will additionally to normal debug information also log the ws responses
        """

        self._CLIENT_TYPE = "user"
        super().__init__(token=token,
                         client_type=self._CLIENT_TYPE,
                         event_loop=event_loop,
                         heartbeat=heartbeat,
                         event_handler=event_handler,
                         close_timeout=close_timeout,
                         log_ws_output=log_ws_output,
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

    async def cancel_friend_request(self, user: typing.Union[int, types.User] = None) -> bool:
        """
        Cancels an open friend request if it exists
        
        :param user: Int or User Object used for the request
        :return: True if the request was successful else False
        """
        try:
            if type(user) is int:
                user_id = str(user)  # ID must be in string format
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))  # ID must be in string format
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.delete(endpoint=f"/relationships/@me/friend-requests/{user_id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to cancel the friend request of a user with id {user_id}! \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def fetch_current_friend_requests(self) -> typing.Union[dict, None]:
        """
        Fetches all open friend requests on Hiven
        
        :return: Returns a dict with all active friend requests
        """
        try:
            resp = await self.http.request(endpoint=f"/relationships/@me/friend-requests")

            if resp.get('success', False):
                data = resp.get('data')

                incoming_ = data.get('incoming')
                if incoming_:
                    data['incoming'] = []
                    for d in incoming_:
                        data['incoming'].append(await types.LazyUser.from_dict(d, self.http))

                outgoing_ = data.get('outgoing')
                if outgoing_:
                    data['outgoing'] = []
                    for d in outgoing_:
                        data['outgoing'].append(await types.LazyUser.from_dict(d, self.http))

                return {
                    'incoming': data['incoming'],
                    'outgoing': data['outgoing']
                }
            else:
                return None

        except Exception as e:
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to fetch the current open friend requests: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def block_user(self, user: typing.Union[int, types.User] = None) -> bool:
        """
        Blocks a user on Hiven

        :param user: Int or User Object used for the request
        :return: True if the request was successful else False
        """
        try:
            if type(user) is int:
                user_id = str(user)  # ID must be in string format
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))  # ID must be in string format
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.put(endpoint=f"/relationships/@me/blocked/{user_id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to block user with id {user_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def unblock_user(self, user: typing.Union[int, types.User] = None) -> bool:
        """
        Unblocks a user if the user is blocked
        
        :param user: Int or User Object used for the request
        :return: True if the request was successful else False
        """
        try:
            if type(user) is int:
                user_id = str(user)  # ID must be in string format
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))  # ID must be in string format
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.delete(endpoint=f"/relationships/@me/blocked/{user_id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to unblock a user with id {user_id}: \n"
                                       f" {e}")
            return False

    async def send_friend_request(self, user: typing.Union[int, types.User] = None) -> bool:
        """
        Sends a friend request to a user
        
        :param user: Int or User Object used for the request
        :return: True if the request was successful else False
        """
        try:
            if type(user) is int:
                user_id = str(user)  # ID must be in string format
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))  # ID must be in string format
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.post(endpoint=f"/relationships/@me/friend-requests",
                                        json={'user_id': f'{user_id}'})

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(msg="[USERCLIENT] Traceback:",
                                suffix=f"Failed to send a friend request a user with id {user_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False
