# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import asyncio
import typing
import fastjsonschema

from . import HivenTypeObject, check_valid
from . import message
from .. import utils
from ..exceptions import InitializationError, InvalidPassedDataError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import User, Message
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['PrivateGroupRoom', 'PrivateRoom']


class PrivateGroupRoom(HivenTypeObject):
    """ Represents a private group chat room with multiple users """
    json_schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'last_message_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'},
                ],
                'default': None
            },
            'recipients': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'}
                ],
                'default': {},
            },
            'name': {'default': None},
            'description': {'default': None},
            'emoji': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'type': {'type': 'integer'},
            'permission_overrides': {'default': None},
            'default_permission_override': {'default': None},
            'position': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'owner_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'house_id': {'type': 'null'} # weird hiven bug
        },
        'additionalProperties': False,
        'required': ['id', 'recipients', 'type']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            self._id = data.get('id')
            self._last_message_id = data.get('last_message_id')
            self._recipients = data.get('recipients')
            self._name = data.get('name')
            self._description = data.get('description')
            self._emoji = data.get('emoji')
            self._type = data.get('type')
            self._client_user = client.client_user

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{self.__class__.__name__}' Validation:",
                suffix=f"Failed to initialise {self.__class__.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {self.__class__.__name__} due to an exception occurring"
            ) from e
        else:
            self._client = client

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipients),
            ('type', self.type)
        ]
        return '<PrivateGroupRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Optional[dict]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['rooms']['private']['multi'][self.id]

    @classmethod
    @check_valid
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        data = cls.validate(data)
        data['name'] = f"Private chat with {data['recipients'][0]['name']}"

        if type(data.get('recipients')) is list:
            data['recipients'] = [i['id'] for i in data['recipients']]

        return data

    @property
    def client_user(self) -> User:
        return getattr(self, '_client_user', None)

    @property
    def recipients(self) -> typing.Optional[typing.List[User]]:
        from . import User
        if utils.convertible(int, self._recipients):
            recipients = []
            for id_ in self._recipients:
                user_data = User.format_obj_data(self._client.storage['users'][id_])
                recipients.append(User(user_data, self._client))

            self._recipients = recipients

        elif type(self._recipients) is User:
            return self._recipients
        else:
            return None

    @property
    def id(self) -> str:
        return getattr(self, '_id', None)

    @property
    def last_message_id(self) -> str:
        return getattr(self, '_last_message_id', None)

    @property
    def name(self) -> str:
        return getattr(self, '_name', None)

    @property
    def description(self) -> int:
        return getattr(self, '_description', None)

    @property
    def emoji(self) -> str:
        return getattr(self, '_emoji', None)

    @property
    def type(self) -> int:
        return getattr(self, '_type', None)

    async def send(self, content: str, delay: float = None) -> typing.Optional[Message]:
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
                msg="[PRIVATE_GROUP_ROOM] Traceback:",
                suffix=f"Failed to send message in room {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
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
            utils.log_traceback(msg="[PRIVATE_GROUP_ROOM] Traceback:",
                                suffix=f"Failed to start call in {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False


class PrivateRoom(HivenTypeObject):
    """ Represents a private chat room with only one user """
    json_schema = PrivateGroupRoom.json_schema
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            self._id = data.get('id')
            self._last_message_id = data.get('last_message_id')
            self._recipient = data.get('recipient')
            self._recipient_id = data.get('recipient_id')
            self._name = data.get('name')
            self._description = data.get('description')
            self._emoji = data.get('emoji')
            self._type = data.get('type')
            self._client_user = client.client_user

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{self.__class__.__name__}' Validation:",
                suffix=f"Failed to initialise {self.__class__.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {self.__class__.__name__} due to an exception occurring"
            ) from e
        else:
            self._client = client

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipient),
            ('type', self.type)
        ]
        return '<PrivateRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Optional[dict]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['rooms']['private']['single'][self.id]

    @classmethod
    @check_valid
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        data = cls.validate(data)

        name = ""
        if not data.get('recipient_id') and data.get('recipients'):
            recipient = data.pop('recipients')[0]
            if type(recipient) is dict:
                name = recipient.get('name', None)
                recipient = recipient.get('id', None)
            elif isinstance(recipient, HivenTypeObject):
                name = getattr(recipient, 'name', None)
                recipient = getattr(recipient, 'id', None)
            else:
                recipient = None
                name = None

            if recipient is None:
                raise InvalidPassedDataError("The passed recipient/s is/are not in the correct format!", data=data)
            else:
                data['recipient_id'] = recipient

        data['recipient'] = data['recipient_id']

        # If the passed recipient object does not contain the name parameter it will be fetched later from the client
        # based on the id
        if name:
            data['name'] = f"Private chat with {name}"
        else:
            data['name'] = None
        return data

    @property
    def name(self) -> typing.Optional[str]:
        if type(self._name) is None:
            self._name = f"Private chat with {self.recipient.name}"
            return self._name
        elif type(self._name) is str:
            return self._name
        else:
            return None

    @property
    def client_user(self) -> User:
        return getattr(self, '_client_user', None)

    @property
    def recipient_id(self) -> str:
        return getattr(self, '_recipient_id', None)

    @property
    def recipient(self) -> typing.Optional[User]:
        from . import User
        if type(self._recipient) is str:
            recipient_id = self._recipient
        elif type(self.recipient_id) is str:
            recipient_id = self.recipient_id
        else:
            recipient_id = None

        if type(self._recipient) is str:
            self._recipient = User(
                data=self._client.storage['users'][recipient_id], client=self._client
            )
            return self._recipient
        elif type(self._recipient) is User:
            return self._recipient
        else:
            return None
    
    @property
    def id(self) -> str:
        return getattr(self, '_id', None)

    @property
    def description(self) -> str:
        return getattr(self, '_description', None)

    @property
    def emoji(self) -> str:
        return getattr(self, '_emoji', None)

    @property
    def last_message_id(self) -> str:
        return getattr(self, '_last_message_id', None)

    @property
    def type(self) -> int:
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
                msg="[PRIVATE_ROOM] Traceback:",
                suffix=f"Failed to start call in room {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return False             

    async def send(self, content: str, delay: float = None) -> typing.Optional[Message]:
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
                msg="[PRIVATE_ROOM] Traceback:",
                suffix=f"Failed to send message in room {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return None
