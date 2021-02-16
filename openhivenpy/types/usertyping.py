import datetime
import logging
import sys
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from . import HivenObject
from .. import utils
from .. import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['UserTyping']


class UserTypingSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    author = fields.Raw(required=True)
    room = fields.Raw(required=True)
    house = fields.Raw(allow_none=True)
    author_id = fields.Int(required=True)
    house_id = fields.Int(allow_none=True)
    room_id = fields.Int(required=True)
    timestamp = fields.Raw(required=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new UserTyping Object
        """
        return UserTyping(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = UserTypingSchema()


class UserTyping(HivenObject):
    """
    Represents a Hiven User Typing in a room
    """
    def __init__(self, **kwargs):
        self._author = kwargs.get('author')
        self._room = kwargs.get('room')
        self._house = kwargs.get('house')
        self._author_id = kwargs.get('author_id')
        self._house_id = kwargs.get('house_id')
        self._room_id = kwargs.get('room_id')
        self._timestamp = kwargs.get('timestamp')

    def __repr__(self) -> str:
        info = [
            ('house_id', self.house_id),
            ('author_id', self.author_id),
            ('room_id', self.room_id),
            ('author', repr(self.author))
        ]
        return '<Typing {}>'.format(' '.join('%s=%s' % t for t in info))

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        http,
                        user,
                        room,
                        house):
        """
        Creates an instance of the Relationship Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param user: The user typing
        :param room: The room where the user is typing
        :param house: The house if the room is a house-room else private_room
        :return: The newly constructed Relationship Instance
        """
        try:
            data['author'] = user
            data['house'] = house
            data['room'] = room
            data['author_id'] = utils.convert_value(int, data.get('author_id'))
            data['house_id'] = utils.convert_value(int, data.get('house_id'))
            data['room_id'] = utils.convert_value(int, data.get('room_id'))

            timestamp = data.get('timestamp')
            # Converting to seconds because it's in milliseconds
            if utils.convertible(int, timestamp):
                data['timestamp'] = datetime.datetime.fromtimestamp(utils.convert_value(int, timestamp))
            else:
                data['timestamp'] = timestamp

            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise errs.InvalidPassedDataError(data=data)

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise errs.InitializationError(f"Failed to initialise {cls.__name__} due to exception:\n"
                                           f"{sys.exc_info()[0].__name__}: {e}!")
        else:
            # Adding the http attribute for API interaction
            instance._http = http

            return instance

    @property
    def timestamp(self) -> datetime.datetime:
        return self._timestamp

    @property
    def author(self):
        return self._author

    @property
    def house(self):
        return self._house

    @property
    def room(self):
        return self._room

    @property
    def author_id(self):
        return self._author_id

    @property
    def house_id(self):
        return self._house_id

    @property
    def room_id(self):
        return self._room_id
