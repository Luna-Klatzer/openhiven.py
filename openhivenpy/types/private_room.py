"""
PrivateRoom File which implements the Hiven GroupPrivateRoom and PrivateRoom
type and its methods (endpoints)

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
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import asyncio
import logging
import sys
from typing import Optional, List
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from . import message
from .hiven_type_schemas import PrivateRoomSchema, get_compiled_validator
from .. import utils
from ..base_types import DataClassObject
from ..exceptions import InvalidPassedDataError
from ..utils import log_type_exception

if TYPE_CHECKING:
    from . import User, Message
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['PrivateGroupRoom', 'PrivateRoom']


class PrivateGroupRoom(DataClassObject):
    """ Represents a private group chat room with multiple users """
    _json_schema: dict = PrivateRoomSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('PrivateGroupRoom')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._id = data.get('id')
        self._last_message_id = data.get('last_message_id')
        self._recipients = data.get('recipients')
        self._name = data.get('name')
        self._description = data.get('description')
        self._emoji = data.get('emoji')
        self._type = data.get('type')
        self._client_user = client.client_user
        self._client = client

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipients),
            ('type', self.type)
        ]
        return '<PrivateGroupRoom {}>'.format(
            ' '.join('%s=%s' % t for t in info)
        )

    def get_cached_data(self) -> Optional[dict]:
        """
        Fetches the most recent data from the cache based on the instance id.

        If updated while the object exists, the data might differentiate, due
        to the object not being updated unlike the cache.
        """
        return self._client.storage['rooms']['private']['group'][self.id]

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be 
        required for the creation of an instance.


        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a
         new class instance
        """
        data = cls.validate(data)
        data['name'] = f"Private chat with {data['recipients'][0]['name']}"

        rep = data.get('recipients')
        id_list: List[str] = []
        if type(rep) is list:
            for user in rep:
                if type(user) is dict:
                    id_list += str(user.get('id', None))
                elif isinstance(user, DataClassObject):
                    id_list += str(getattr(user, 'id', None))
                else:
                    raise InvalidPassedDataError(
                        "The passed recipient is not in the correct "
                        "format!",
                        data=data
                    )
        else:
            raise InvalidPassedDataError(
                "The passed recipients are not in the correct format!",
                data=data
            )
        data['recipients'] = id_list
        return data

    @property
    def client_user(self) -> Optional[User]:
        """ Returns the Client User inside this PrivateGroupRoom """
        return getattr(self, '_client_user', None)

    @property
    def recipients(self) -> Optional[List[User]]:
        """ Returns a list of all recipients """
        from . import User
        if utils.convertible(int, self._recipients):
            recipients = []
            for id_ in self._recipients:
                data = self._client.storage['users'].get(id_)
                if data:
                    user_data = User.format_obj_data(data)
                    recipients.append(User(user_data, self._client))
                else:
                    recipients.append(None)

            self._recipients = recipients

        elif type(self._recipients) is User:
            return self._recipients
        else:
            return None

    @property
    def id(self) -> Optional[str]:
        """ Returns the id of the PrivateGroupRoom """
        return getattr(self, '_id', None)

    @property
    def last_message_id(self) -> Optional[str]:
        """ Returns the id of the last message inside the PrivateGroupRoom """
        return getattr(self, '_last_message_id', None)

    @property
    def name(self) -> Optional[str]:
        """ Returns the name of the PrivateGroupRoom """
        return getattr(self, '_name', None)

    @property
    def description(self) -> Optional[int]:
        """ Returns the description of the PrivateGroupRoom """
        return getattr(self, '_description', None)

    @property
    def emoji(self) -> Optional[str]:
        """ Returns the emoji of this PrivateGroupRoom if it exists """
        return getattr(self, '_emoji', None)

    @property
    def type(self) -> Optional[int]:
        """ Returns the type of this PrivateGroupRoom """
        return getattr(self, '_type', None)

    # TODO! Implement Base Room class (ABC)
    async def send(
            self, content: str, delay: float = None
    ) -> Optional[Message]:
        """
        Sends a message in the private room.

        :param content: Content of the message
        :param delay: Seconds to wait until sending the message (in seconds)
        :return: A Message instance if successful else None
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)
            resp = await self._client.http.post(
                endpoint=f"/rooms/{self.id}/messages",
                json={"content": content}
            )

            raw_data = await resp.json()

            # Raw_data not in correct format => needs to access data field
            data = raw_data.get('data')

            data = message.Message.format_obj_data(data)
            msg = message.Message(data, self._client)
            return msg

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to send message in room {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return None

    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateGroupRoom.start_call()

        Starts a call with the user in the private room

        :param delay: Delay until calling (in seconds)
        :return: True if successful
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)
            await self._client.http.post(f"/rooms/{self.id}/call")
            return True

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to start call in {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return False


class PrivateRoom(DataClassObject):
    """ Represents a private chat room with only one user """
    _json_schema: dict = PrivateRoomSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('PrivateRoom')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._id = data.get('id')
        self._last_message_id = data.get('last_message_id')
        self._recipient = data.get('recipient')
        self._recipient_id = data.get('recipient_id')
        self._name = data.get('name')
        self._description = data.get('description')
        self._emoji = data.get('emoji')
        self._type = data.get('type')
        self._client_user = client.client_user

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipient),
            ('type', self.type)
        ]
        return '<PrivateRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> Optional[dict]:
        """
        Fetches the most recent data from the cache based on the instance id.

        If updated while the object exists, the data might differentiate, due
        to the object not being updated unlike the cache.
        """
        return self._client.storage['rooms']['private']['single'][self.id]

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be 
        required for the creation of an instance.


        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a
         new class instance
        """
        data = cls.validate(data)

        name = ""
        if not data.get('recipient_id') and data.get('recipients'):
            recipient = data.pop('recipients')[0]
            if type(recipient) is dict:
                name = recipient.get('name', None)
                recipient = recipient.get('id', None)
            elif isinstance(recipient, DataClassObject):
                name = getattr(recipient, 'name', None)
                recipient = getattr(recipient, 'id', None)
            else:
                recipient = None
                name = None

            if recipient is None:
                raise InvalidPassedDataError(
                    "The passed recipient/s is/are not in the correct format!",
                    data=data
                )
            else:
                data['recipient_id'] = recipient

        data['recipient'] = data['recipient_id']

        # If the passed recipient object does not contain the name parameter
        # it will be fetched later from the client based on the id
        if name:
            data['name'] = f"Private chat with {name}"
        else:
            data['name'] = None
        return data

    @property
    def name(self) -> Optional[str]:
        """ Name of the PrivateRoom """
        if type(self._name) is None:
            self._name = f"Private chat with {self.recipient.name}"
            return self._name
        elif type(self._name) is str:
            return self._name
        else:
            return None

    @property
    def client_user(self) -> Optional[User]:
        """ Returns the client_user of this class """
        return getattr(self, '_client_user', None)

    @property
    def recipient_id(self) -> Optional[str]:
        """ The ID of the recipient """
        return getattr(self, '_recipient_id', None)

    @property
    def recipient(self) -> Optional[User]:
        """ Returns the recipient object instance """
        from . import User
        if type(self._recipient) is str:
            recipient_id = self._recipient
        elif type(self.recipient_id) is str:
            recipient_id = self.recipient_id
        else:
            recipient_id = None

        if type(self._recipient) is str:
            data = self._client.storage['users'].get(recipient_id)
            if data:
                self._recipient = User(data=data, client=self._client)
                return self._recipient
            else:
                return None

        elif type(self._recipient) is User:
            return self._recipient
        else:
            return None

    @property
    def id(self) -> Optional[str]:
        """ Returns the id of the PrivateRoom """
        return getattr(self, '_id', None)

    @property
    def description(self) -> Optional[str]:
        """ Return the description of the PrivateRoom """
        return getattr(self, '_description', None)

    @property
    def emoji(self) -> Optional[str]:
        """ The emoji of the PrivateRoom, if it has one """
        return getattr(self, '_emoji', None)

    @property
    def last_message_id(self) -> Optional[str]:
        """ The id of the last sent message """
        return getattr(self, '_last_message_id', None)

    @property
    def type(self) -> Optional[int]:
        """ The type of the PrivateRoom """
        return getattr(self, '_type', None)

    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateRoom.start_call()

        Starts a call with the user in the private room
    
        :param delay: Delay until calling (in seconds)
        :return: True if successful
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)

            resp = await self._client.http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data'):
                return True
            else:
                return False

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to start call in room {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return False

    # TODO! Implement Base Room class (ABC)
    async def send(
            self, content: str, delay: float = None
    ) -> Optional[Message]:
        """
        Sends a message in the private room. 

        :param content: Content of the message
        :param delay: Delay until sending the message (in seconds)
        :return: Returns a Message Instance if successful.
        """
        # TODO! Requires functionality check!
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)
            resp = await self._client.http.post(
                endpoint=f"/rooms/{self.id}/messages", json={"content": content}
            )

            raw_data = await resp.json()

            # Raw_data not in correct format => needs to access data field
            data = raw_data.get('data')

            data = message.Message.format_obj_data(data)
            msg = message.Message(data, self._client)
            return msg

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to send message in room {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return None
