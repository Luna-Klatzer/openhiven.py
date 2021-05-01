import logging
import sys
from typing import Union, overload

from .hivenclient import HivenClient
from .. import types
from .. import utils
from ..exceptions import HTTPFailedRequestError

__all__ = ['UserClient']

logger = logging.getLogger(__name__)


class UserClient(HivenClient):
    """ Class for the specific use of a user account on Hiven """

    @overload
    async def cancel_friend_request(self, user: types.User) -> bool:
        ...

    @overload
    async def cancel_friend_request(self, user: int) -> bool:
        ...

    async def cancel_friend_request(self, user) -> bool:
        """
        Cancels an open friend request if it exists
        
        :param user: Int or User Object used for the request
        :return: True if the request was successful else it will raise an exception
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected openhivenpy.types.User or int! Not {type(user)}")

            resp = await self.http.delete(endpoint=f"/relationships/@me/friend-requests/{user_id}")
            return True

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to cancel the friend request of a user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise

    async def fetch_current_friend_requests(self) -> Union[dict, None]:
        """
        Fetches all open friend requests on Hiven
        
        :return: Returns a dict with all active friend requests if successful else it will raise an exception
        """
        try:
            resp = await self.http.get(endpoint=f"/relationships/@me/friend-requests")
            resp = await resp.json()

            data = resp.get('data')

            incoming_ = data.get('incoming')
            if incoming_:
                data['incoming'] = []
                for d in incoming_:
                    data['incoming'].append(types.LazyUser(d, self))

            outgoing_ = data.get('outgoing')
            if outgoing_:
                data['outgoing'] = []
                for d in outgoing_:
                    data['outgoing'].append(types.LazyUser(d, self))

            return {
                'incoming': data['incoming'],
                'outgoing': data['outgoing']
            }

        except Exception as e:
            utils.log_traceback(
                brief="Failed to fetch the current open friend requests:",
                exc_info=sys.exc_info()
            )
            raise

    @overload
    async def block_user(self, user: types.User) -> bool:
        ...

    @overload
    async def block_user(self, user: int) -> bool:
        ...

    async def block_user(self, user) -> bool:
        """
        Blocks a user on Hiven

        :param user: Int or User Object used for the request
        :return: True if the request was successful else it will raise an exception
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.put(endpoint=f"/relationships/@me/blocked/{user_id}")

            return True

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to block user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise

    @overload
    async def unblock_user(self, user: types.User) -> bool:
        ...

    @overload
    async def unblock_user(self, user: int) -> bool:
        ...

    async def unblock_user(self, user) -> bool:
        """
        Unblocks a user if the user is blocked
        
        :param user: Int or User Object used for the request
        :return: True if the request was successful else it will raise an exception
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.delete(endpoint=f"/relationships/@me/blocked/{user_id}")
            return True

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to unblock a user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise

    @overload
    async def send_friend_request(self, user: types.User) -> bool:
        ...

    @overload
    async def send_friend_request(self, user: int) -> bool:
        ...

    async def send_friend_request(self, user) -> bool:
        """
        Sends a friend request to a user
        
        :param user: Int or User Object used for the request
        :return: True if the request was successful else it will raise an exception
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.http.post(
                endpoint=f"/relationships/@me/friend-requests", json={'user_id': f'{user_id}'}
            )

            if resp.status < 300:
                return True
            else:
                raise HTTPFailedRequestError()

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to send a friend request a user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise
