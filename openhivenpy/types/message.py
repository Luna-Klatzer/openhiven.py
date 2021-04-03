# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import datetime
import logging
import sys
import asyncio
import types
import typing

import fastjsonschema

from . import HivenObject, check_valid
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError, HTTPForbiddenError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .embed import Embed
    from .room import Room
    from .user import User
    from .house import House
    from .mention import Mention
    from .attachment import Attachment

logger = logging.getLogger(__name__)

__all__ = ['DeletedMessage', 'Message']


class DeletedMessage(HivenObject):
    """ Represents a Deleted Message """
    schema = {
        'type': 'object',
        'properties': {
            'message_id': {'type': 'string'},
            'house_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'room_id': {'type': 'string'}
        },
        'additionalProperties': False,
        'required': ['message_id', 'room_id']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._message_id = utils.safe_convert(int, kwargs.get('message_id'))
        self._house_id = utils.safe_convert(int, kwargs.get('house_id'))
        self._room_id = utils.safe_convert(int, kwargs.get('room_id'))

    def __str__(self):
        return f"Deleted message in room {self.room_id}"

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data['message_id'] = data['id']
        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the DeletedMessage Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed DeletedMessage Instance
        """
        try:
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
    def message_id(self):
        return getattr(self, '_message_id')

    @property
    def house_id(self):
        return getattr(self, '_house_id')

    @property
    def room_id(self):
        return getattr(self, '_room_id')


class Message(HivenObject):
    """
    Data Class for a standard Hiven message
    """
    schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'author': {'type': 'object'},
            'author_id': {'type': 'string'},
            'attachment': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
                'default': {},
            },
            'content': {'type': 'string'},
            'timestamp': {'type': 'string'},
            'edited_at': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'mentions': {
                'type': 'array',
                'default': []
            },
            'type': {'type': 'integer'},
            'exploding': {
                'anyOf': [
                    {'type': 'boolean'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'house_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'room_id': {'type': 'string'},
            'embed': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'bucket': {
                'anyOf': [
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'device_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'exploding_age': {'default': None}
        },
        'additionalProperties': False,
        'required': ['id', 'author', 'author_id', 'content', 'timestamp', 'type', 'mentions', 'room_id']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._author = kwargs.get('author')
        self._author_id = kwargs.get('author_id')
        self._attachment = kwargs.get('attachment')
        self._content = kwargs.get('content')
        self._timestamp = kwargs.get('timestamp')
        self._edited_at = kwargs.get('edited_at')
        self._mentions = kwargs.get('mentions')
        self._type = kwargs.get('type')  # I believe, 0 = normal message, 1 = system.
        self._exploding = kwargs.get('exploding')
        self._house_id = kwargs.get('house_id')
        self._house = kwargs.get('house')
        self._room_id = kwargs.get('room_id')
        self._room = kwargs.get('room')
        self._embed = kwargs.get('embed')
        self._bucket = kwargs.get('bucket')
        self._device_id = kwargs.get('device_id')
        self._exploding_age = kwargs.get('exploding_age')

    def __str__(self) -> str:
        return f"<Message id='{self.id}' from '{self.author.name}'>"

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('content', self.content),
            ('author', repr(self.author)),
            ('room', repr(self.room)),
            ('type', self.type),
            ('exploding', self.exploding),
            ('edited_at', self.edited_at)
        ]
        return '<Message {}>'.format(' '.join('%s=%s' % t for t in info))

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
        data['type'] = utils.safe_convert(int, data.get('type'), None)  # I believe, 0 = normal message, 1 = system.
        data['bucket'] = utils.safe_convert(int, data.get('bucket'), None)
        data['exploding_age'] = utils.safe_convert(int, data.get('exploding_age'), None)

        timestamp = data.get('timestamp')
        # Converting to seconds because it's in milliseconds
        if utils.convertible(int, timestamp):
            data['timestamp'] = datetime.datetime.fromtimestamp(utils.safe_convert(int, timestamp) / 1000)
        else:
            data['timestamp'] = timestamp

        data = cls.validate(data)

        room_ = data.get('room')
        if room_:
            if type(room_) is dict:
                room_ = room_.get('id', None)
            elif isinstance(room_, HivenObject):
                room_ = getattr(room_, 'id', None)

            if room_ is None:
                raise InvalidPassedDataError("The passed room is not in the correct format!", data=data)
            else:
                data['room'] = room_

        house_ = data.get('house')
        if house_:
            if type(house_) is dict:
                house_ = house_.get('id', None)
            elif isinstance(house_, HivenObject):
                house_ = getattr(house_, 'id', None)

            if house_ is None:
                raise InvalidPassedDataError("The passed house is not in the correct format!", data=data)
            else:
                data['house'] = house_

        author = data.get('author')
        if author:
            if type(author) is dict:
                author = author.get('id', None)
            elif isinstance(author, HivenObject):
                author = getattr(author, 'id', None)

            if author is None:
                raise InvalidPassedDataError("The passed author is not in the correct format!", data=data)
            else:
                data['author'] = author

        data['device_id'] = utils.safe_convert(str, data.get('device_id'), None)
        if data.get('attachment'):
            from .attachment import Attachment
            data['attachment'] = Attachment.format_obj_data(data.get('attachment'))
        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the Message Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Message Instance
        """
        try:
            from .embed import Embed
            from .room import Room
            from .user import User
            from .house import House
            from .mention import Mention
            from .attachment import Attachment

            # TODO! Data needs to be added correctly
            if data.get('house'):
                house_data = client.storage['houses'][data['house_id']]
                data['house'] = await House.create_from_dict(house_data, client=client)

            room_data = client.storage['rooms'][data['room_id']]
            data['room'] = await Room.create_from_dict(room_data, client=client)

            author_data = client.storage['houses'][data['house_id']]['members'][data['author']['id']]
            data['author'] = await User.create_from_dict(author_data, client=client)

            if data.get('embed'):
                data['embed'] = await Embed.create_from_dict(data.get('embed'), client)

            mentions_ = []
            for d in data.get('mentions', []):
                dict_ = {
                    'timestamp': data['timestamp'],
                    'author': data['author'],
                    'user': d
                }
                mention_data = Mention.format_obj_data(dict_)
                mentions_.append(await Mention.create_from_dict(mention_data, client=client))
            data['mentions'] = mentions_

            if data.get('attachment'):
                attachment_data = data.get('attachment')
                data['attachment'] = await Attachment.create_from_dict(attachment_data, client=client)

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
    def id(self) -> str:
        return getattr(self, '_id', None)

    @property
    def author_id(self) -> str:
        return getattr(self, '_author_id', None)

    @property
    def author(self) -> User:
        return getattr(self, '_author', None)

    @property
    def created_at(self) -> str:
        return getattr(self, '_created_at', None)

    @property
    def type(self) -> int:
        return getattr(self, '_type', None)

    @property
    def exploding(self) -> bool:
        return getattr(self, '_exploding', None)

    @property
    def edited_at(self) -> str:
        return getattr(self, '_edited_at', None)

    @property
    def room(self) -> Room:
        return getattr(self, '_room', None)

    @property
    def house(self) -> House:
        return getattr(self, '_house', None)

    @property
    def attachment(self) -> Attachment:
        return getattr(self, '_attachment', None)

    @property
    def content(self) -> str:
        return getattr(self, '_content', None)

    @property
    def mentions(self) -> typing.List[Mention]:
        return getattr(self, '_mentions', None)

    @property
    def room_id(self) -> str:
        return getattr(self, '_room_id', None)

    @property
    def house_id(self) -> str:
        return getattr(self, '_house_id', None)

    @property
    def embed(self) -> Embed:
        return getattr(self, '_embed', None)

    @property
    def bucket(self) -> int:
        return getattr(self, '_bucket', None)

    @property
    def device_id(self) -> str:
        return getattr(self, '_device_id', None)

    @property
    def exploding_age(self) -> int:
        return getattr(self, '_exploding_age', None)

    async def mark_as_read(self, delay: float = None) -> bool:
        """
        Marks the message as read. This doesn't need to be done for bot clients.
        
        :param delay: Delay until marking the message as read (in seconds)
        :return: True if the request was successful else False
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)
            await self._client.http.post(endpoint=f"/rooms/{self.room_id}/messages/{self.id}/ack")
            return True

        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to mark message as read {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def delete(self, delay: float = None) -> bool:
        """
        Deletes the message. Raises Forbidden if not allowed.
        
        :param delay: Delay until deleting the message as read (in seconds)
        :return: A DeletedMessage object if successful
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)

            resp = await self._client.http.delete(endpoint=f"/rooms/{self.room_id}/messages/{self.id}")

            if not resp.status < 300:
                raise HTTPForbiddenError()
            else:
                return True

        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to delete the message {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def edit(self, content: str) -> bool:
        """
        Edits a message on Hiven
            
        :return: True if the request was successful else False
        """
        try:
            await self._client.http.patch(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}", json={'content': content}
            )
            return True

        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to edit message {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False
