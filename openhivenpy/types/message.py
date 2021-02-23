import datetime
import logging
import sys
import asyncio
import types
import typing

import fastjsonschema

from . import HivenObject
from . import user
from . import mention
from . import embed
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError, HTTPResponseError, HTTPForbiddenError

logger = logging.getLogger(__name__)

__all__ = ['DeletedMessage', 'Message']


class DeletedMessage(HivenObject):
    """ Represents a Deleted Message """
    schema = {
        'type': 'object',
        'properties': {
            'message_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'}
                ]
            },
            'house_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'room_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'}
                ]
            },
        },
        'additionalProperties': False,
        'required': ['message_id', 'room_id']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    @classmethod
    def validate(cls, data, *args, **kwargs):
        try:
            return cls.json_validator(data, *args, **kwargs)
        except Exception as e:
            utils.log_validation_traceback(cls, data, e)
            raise

    def __init__(self, **kwargs):
        self._message_id = utils.convert_value(int, kwargs.get('message_id'))
        self._house_id = utils.convert_value(int, kwargs.get('house_id'))
        self._room_id = utils.convert_value(int, kwargs.get('room_id'))

    def __str__(self):
        return f"Deleted message in room {self.room_id}"

    @classmethod
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data['message_id'] = int(data['id'])
        data['house_id'] = utils.convert_value(int, data['house_id'])
        data['room_id'] = int(data['room_id'])
        return data

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the DeletedMessage Class with the passed data

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
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
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
            'id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'}
                ]
            },
            'author': {'type': 'object'},
            'author_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'}
                ]
            },
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
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'house_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'room_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                ]
            },
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

    @classmethod
    def validate(cls, data, *args, **kwargs):
        try:
            return cls.json_validator(data, *args, **kwargs)
        except Exception as e:
            utils.log_validation_traceback(cls, data, e)
            raise

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
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data['house'] = data['house']['id']
        data['room'] = data['room']['id']
        data['author'] = data['author']['id']
        data['attachment'] = data.get('attachment')
        data['content'] = data.get('content')
        data['edited_at'] = data.get('edited_at')
        data['type'] = utils.convert_value(int, data.get('type'))  # I believe, 0 = normal message, 1 = system.
        data['exploding'] = data.get('exploding')
        data['bucket'] = utils.convert_value(int, data.get('bucket'))
        data['device_id'] = utils.convert_value(int, data.get('device_id'))
        data['exploding_age'] = utils.convert_value(int, data.get('exploding_age'))
        data['author_id'] = utils.convert_value(int, data.get('author_id'))

        timestamp = data.get('timestamp')
        # Converting to seconds because it's in milliseconds
        if utils.convertible(int, timestamp):
            data['timestamp'] = datetime.datetime.fromtimestamp(utils.convert_value(int, timestamp) / 1000)
        else:
            data['timestamp'] = timestamp

        data = cls.validate(data)
        data['id'] = utils.convert_value(int, data.get('id'))
        data['house_id'] = utils.convert_value(int, data.get('house_id'))
        data['room_id'] = utils.convert_value(int, data.get('room_id'))
        data['house'] = utils.convert_value(int, data['house']['id'])
        data['room'] = utils.convert_value(int, data['room']['id'])
        data['author'] = utils.convert_value(int, data['author']['id'])
        return data

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the Message Class with the passed data

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Message Instance
        """
        try:
            data['house'] = client.storage['houses'][data['house_id']]
            data['room'] = client.storage['rooms'][data['room_id']]
            data['author'] = client.storage['houses'][data['house_id']]['members']['']
            data['embed'] = await embed.Embed.from_dict(data.get('embed'), client) if data.get('embed') else None
            mentions_ = []
            for d in data.get('mentions', []):
                mentions_.append(
                    await mention.Mention.from_dict(
                        {
                            'timestamp': data['timestamp'],
                            'author': data['author'],
                            'user': d
                        }, client)
                )
            data['mentions'] = mentions_

            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!")
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def id(self) -> int:
        return getattr(self, '_id', None)

    @property
    def author_id(self) -> int:
        return getattr(self, '_author_id', None)

    @property
    def author(self):
        return getattr(self, '_author', None)

    @property
    def created_at(self):
        return getattr(self, '_created_at', None)

    @property
    def type(self):
        return getattr(self, '_type', None)

    @property
    def exploding(self):
        return getattr(self, '_exploding', None)

    @property
    def edited_at(self):
        return getattr(self, '_edited_at', None)

    @property
    def room(self):
        return getattr(self, '_room', None)

    @property
    def house(self):
        return getattr(self, '_house', None)

    @property
    def attachment(self):
        return getattr(self, '_attachment', None)

    @property
    def content(self):
        return getattr(self, '_content', None)

    @property
    def mentions(self):
        return getattr(self, '_mentions', None)

    @property
    def room_id(self):
        return getattr(self, '_room_id', None)

    @property
    def house_id(self):
        return getattr(self, '_house_id', None)

    @property
    def embed(self):
        return getattr(self, '_embed', None)

    @property
    def bucket(self):
        return getattr(self, '_bucket', None)

    @property
    def device_id(self):
        return getattr(self, '_device_id', None)

    @property
    def exploding_age(self):
        return getattr(self, '_exploding_age', None)

    async def mark_as_read(self, delay: float = None) -> bool:
        """
        Marks the message as read. This doesn't need to be done for bot clients.
        
        :param delay: Delay until marking the message as read (in seconds)
        :return: True if the request was successful else False
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._client.http.post(endpoint=f"/rooms/{self.room_id}/messages/{self.id}/ack")

            if resp.status < 300:
                return True
            else:
                raise HTTPResponseError

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
            await asyncio.sleep(delay=delay) if delay is not None else None

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
            resp = await self._client.http.patch(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}", json={'content': content}
            )

            if resp.status < 300:
                return True
            else:
                raise HTTPResponseError("Unknown! See HTTP Logs!")

        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to edit message {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False
