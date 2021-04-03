# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import asyncio
import types
import typing
import fastjsonschema

from . import HivenObject, check_valid
from . import message
from .. import utils
from ..exceptions import InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import User

logger = logging.getLogger(__name__)

__all__ = ['PrivateGroupRoom', 'PrivateRoom']


class PrivateGroupRoom(HivenObject):
    """
    Represents a private group chat room with multiple person
    """
    schema = {
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
            'house_id': {'default': None}
        },
        'additionalProperties': False,
        'required': ['id', 'recipients', 'type']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._last_message_id = kwargs.get('last_message_id')
        self._recipients = kwargs.get('recipients')
        self._name = kwargs.get('name')
        self._description = kwargs.get('description')
        self._emoji = kwargs.get('emoji')
        self._type = kwargs.get('type')
        self._client_user = kwargs.get('client_user')

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipients),
            ('type', self.type)
        ]
        return '<PrivateGroupRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Union[dict, None]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['rooms']['private']['multi'][self.id]

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data['name'] = f"Private chat with {data['recipients'][0]['name']}"

        if type(data.get('recipients')) is list:
            data['recipients'] = [i['id'] for i in data['recipients']]

        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the PrivateGroupRoom Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed PrivateGroupRoom Instance
        """
        try:
            from . import User
            _recipients = []
            for id_ in data.get("recipients"):
                user_data = client.storage['users'][id_]
                _recipients.append(await User.create_from_dict(user_data, client))

            data['recipients'] = _recipients
            data['name'] = f"Private Group chat with: {(', '.join(r.name for r in _recipients))}"
            data['client_user'] = client.user

            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def client_user(self) -> User:
        return getattr(self, '_client_user', None)

    @property
    def recipients(self) -> typing.List[User]:
        return getattr(self, '_recipients', None)
    
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

    async def send(self, content: str, delay: float = None) -> typing.Union[message.Message, None]:
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
            msg = await message.Message.create_from_dict(data, self._client)
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


class PrivateRoom(HivenObject):
    """ Represents a private chat room with a user """
    @classmethod
    def validate(cls, data, *args, **kwargs):
        try:
            return PrivateGroupRoom.json_validator(data, *args, **kwargs)
        except Exception as e:
            utils.log_validation_traceback(cls, data, e)
            raise

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._last_message_id = kwargs.get('last_message_id')
        self._recipient = kwargs.get('recipient')
        self._name = kwargs.get('name')
        self._description = kwargs.get('description')
        self._emoji = kwargs.get('emoji')
        self._type = kwargs.get('type')
        self._client_user = kwargs.get('client_user')

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipient),
            ('type', self.type)
        ]
        return '<PrivateRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Union[dict, None]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['rooms']['private']['single'][self.id]

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data['name'] = f"Private chat with {data['recipients'][0]['name']}"
        data['recipient'] = data.pop('recipients')[0]['id']
        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the PrivateRoom Class with the passed data

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed PrivateRoom Instance
        """
        try:
            from . import User
            user_data = client.storage['users'][data['recipient']['id']]
            data['recipient'] = await User.create_from_dict(user_data, client)
            data['client_user'] = client.user

            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def client_user(self) -> User:
        return getattr(self, '_client_user', None)

    @property
    def recipient(self) -> User:
        return getattr(self, '_recipient', None)
    
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
    def name(self) -> str:
        return getattr(self, '_name', None)

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

    async def send(self, content: str, delay: float = None) -> typing.Union[message.Message, None]:
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
            msg = await message.Message.create_from_dict(data, self._client)
            return msg
        
        except Exception as e:
            utils.log_traceback(
                msg="[PRIVATE_ROOM] Traceback:",
                suffix=f"Failed to send message in room {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return None
