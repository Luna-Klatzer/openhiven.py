import datetime
import logging
import sys
import asyncio
import typing

from marshmallow import Schema, fields, post_load, ValidationError, RAISE, EXCLUDE

from . import HivenObject
from . import user
from . import mention
from . import embed
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['DeletedMessage', 'Message', 'MessageSchema', 'DeletedMessageSchema']


class MessageSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    id = fields.Int(required=True)
    author = fields.Raw(required=True)
    attachment = fields.Raw(default=None, allow_none=True)
    content = fields.Str(required=True)
    timestamp = fields.Raw(required=True)
    edited_at = fields.Raw(default=None, allow_none=True)
    mentions = fields.List(fields.Field(), default=[], allow_none=True)
    type = fields.Int(required=True, allow_none=True)
    exploding = fields.Raw()
    house_id = fields.Int(default=None, allow_none=True)
    house = fields.Raw(default=None, allow_none=True)
    room_id = fields.Int(required=True)
    room = fields.Raw(required=True)
    embed = fields.Raw(default=None, allow_none=True)
    bucket = fields.Raw(default=None, allow_none=True)
    author_id = fields.Int(required=True)
    exploding_age = fields.Raw(allow_none=True)
    device_id = fields.Int(required=True, allow_none=True)


    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Message Object
        """
        return Message(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = MessageSchema()


class DeletedMessageSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    message_id = fields.Int(required=True)
    house_id = fields.Int(required=True)
    room_id = fields.Int(required=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new DeletedMessage Object
        """
        return DeletedMessage(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_DELETED_SCHEMA = DeletedMessageSchema()


class DeletedMessage(HivenObject):
    """
    Represents a Deleted Message
    """
    def __init__(self, **kwargs):
        self._message_id = utils.convert_value(int, kwargs.get('message_id'))
        self._house_id = utils.convert_value(int, kwargs.get('house_id'))
        self._room_id = utils.convert_value(int, kwargs.get('room_id'))

    def __str__(self):
        return f"Deleted message in room {self.room_id}"

    @classmethod
    async def from_dict(cls, data: dict, **kwargs):
        """
        Creates an instance of the DeletedMessage Class with the passed data

        :param data: Dict for the data that should be passed
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed DeletedMessage Instance
        """
        try:
            instance = GLOBAL_DELETED_SCHEMA.load(data, unknown=RAISE)
            return instance

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            return None

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")

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
    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._author = kwargs.get('author')
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
        self._author_id = kwargs.get('author_id')

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
    async def from_dict(cls,
                        data: dict,
                        http,
                        *,
                        author: user.User = None,
                        users: typing.List[user.User] = None,
                        room_: typing.Any = None,
                        rooms: typing.List[typing.Any] = None,
                        houses: typing.List[typing.Any] = [],
                        house_: typing.Any = None,
                        **kwargs):
        """
        Creates an instance of the Message Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param author: The Author of the Message that can be passed if it was already fetched
        :param users: The cached users List to fetch the mentioned users from
        :param room_: The room of the Message
        :param rooms: The cached Room List to fetch the room from
        :param houses: The cached House List to fetch the house from or add ones if passed
        :param house_: The House of the Message that can be passed if it was already fetched
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed Message Instance
        """
        try:
            data['id'] = utils.convert_value(int, data.get('id'))
            data['house_id'] = utils.convert_value(int, data.get('house_id'))
            data['room_id'] = utils.convert_value(int, data.get('room_id'))
            data['house'] = house_ if house_ else utils.get(houses, id=utils.convert_value(int, data['house_id']))
            data['room'] = room_ if room_ else utils.get(rooms, id=utils.convert_value(int, data['room_id']))
            data['author'] = author if author else utils.get(data['house'].members if data['house'] else users,
                                                             id=utils.convert_value(int, data.get('author_id')))
            data['attachment'] = data.get('attachment')
            data['content'] = data.get('content')
            data['edited_at'] = data.get('edited_at')
            data['type'] = utils.convert_value(int, data.get('type'))  # I believe, 0 = normal message, 1 = system.
            data['exploding'] = data.get('exploding')
            data['embed'] = await embed.Embed.from_dict(data.get('embed'), http) if data.get('embed') else None
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

            mentions_ = []
            for d in data.get('mentions', []):
                mentions_.append(await mention.Mention.from_dict({'timestamp': data['timestamp'],
                                                                  'author': data['author'],
                                                                  'user': d},
                                                                 users=users))
            data['mentions'] = mentions_

            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)
            # Adding the http attribute for API interaction
            instance._http = http

            return instance

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            return None

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")

    @property
    def id(self):
        return utils.convert_value(int, self._id)

    @property
    def author(self):
        return self._author

    @property
    def created_at(self):
        return self._timestamp

    @property
    def type(self):
        return self._type

    @property
    def exploding(self):
        return self._exploding

    @property
    def edited_at(self):
        return self._edited_at

    @property
    def room(self):
        return self._room

    @property
    def house(self):
        return self._house

    @property
    def attachment(self):
        return self._attachment

    @property
    def content(self):
        return self._content

    @property
    def mentions(self):
        return self._mentions

    @property
    def room_id(self):
        return self._room_id

    @property
    def house_id(self):
        return self._house_id

    @property 
    def embed(self):
        return self._embed

    @property
    def bucket(self):
        return self._bucket

    @property
    def device_id(self):
        return self._device_id

    @property
    def exploding_age(self):
        return self._exploding_age

    @property
    def author_id(self):
        return self._author_id

    async def mark_as_read(self, delay: float = None) -> bool:
        """
        Marks the message as read. This doesn't need to be done for bot clients.
        
        :param delay: Delay until marking the message as read (in seconds)
        :return: True if the request was successful else False
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(endpoint=f"/rooms/{self.room_id}/messages/{self.id}/ack")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse
        
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
            
            resp = await self._http.delete(endpoint=f"/rooms/{self.room_id}/messages/{self.id}")
            
            if not resp.status < 300:
                raise errs.Forbidden()
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
            resp = await self._http.patch(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}",
                json={'content': content})

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
    
        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to edit message {repr(self)}: \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False
