"""
User-Client File - Class for using a User Account on Hiven

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
import sys
from typing import Union, overload

from .hivenclient import HivenClient
from .. import types
from .. import utils

__all__ = ['UserClient']

logger = logging.getLogger(__name__)


class UserClient(HivenClient):
    """ Class for the specific use of a user account on Hiven """

    @overload
    async def cancel_friend_request(self, user: types.User) -> None:
        ...

    @overload
    async def cancel_friend_request(self, user: int) -> None:
        ...

    async def cancel_friend_request(self, user) -> None:
        """
        Cancels an open friend request if it exists
        
        :param user: Int or User Object used for the request
        :raises TypeError: If the passed user is not one of the types: int or
         types.User
        :raise HTTPError: If any HTTP error is raised while executing
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(
                    f"Expected openhivenpy.types.User or int! Not {type(user)}"
                )

            await self.http.delete(
                f"/relationships/@me/friend-requests/{user_id}"
            )

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to cancel the friend request of a user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise e

    async def fetch_current_friend_requests(self) -> Union[dict, None]:
        """
        Fetches all open friend requests on Hiven
        
        :return: Returns a dict with all active friend requests if successful
        :raise HTTPError: If any HTTP error is raised while executing
        """
        try:
            resp = await self.http.get(f"/relationships/@me/friend-requests")
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
            raise e

    @overload
    async def block_user(self, user: types.User) -> None:
        ...

    @overload
    async def block_user(self, user: int) -> None:
        ...

    async def block_user(self, user) -> None:
        """
        Blocks a user on Hiven

        :param user: Int or User Object used for the request
        :raise HTTPError: If any HTTP error is raised while executing
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            await self.http.put(f"/relationships/@me/blocked/{user_id}")

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to block user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise e

    @overload
    async def unblock_user(self, user: types.User) -> None:
        ...

    @overload
    async def unblock_user(self, user: int) -> None:
        ...

    async def unblock_user(self, user) -> None:
        """
        Unblocks a user if the user is blocked
        
        :param user: Int or User Object used for the request
        :raise HTTPError: If any HTTP error is raised while executing
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            await self.http.delete(
                f"/relationships/@me/blocked/{user_id}"
            )

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to unblock a user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise e

    @overload
    async def send_friend_request(self, user: types.User) -> None:
        ...

    @overload
    async def send_friend_request(self, user: int) -> None:
        ...

    async def send_friend_request(self, user) -> None:
        """
        Sends a friend request to a user
        
        :param user: Int or User Object used for the request
        :raise HTTPError: If any HTTP error is raised while executing
        """
        try:
            if type(user) is int:
                user_id = str(user)
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            await self.http.post(
                endpoint=f"/relationships/@me/friend-requests",
                json={'user_id': user_id}
            )

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(
                brief=f"Failed to send a friend request a user with id {user_id}:",
                exc_info=sys.exc_info()
            )
            raise e
