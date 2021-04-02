import datetime
import logging
import sys
import types
import typing

import fastjsonschema

from . import HivenObject, check_valid
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['UserTyping']


class UserTyping(HivenObject):
    """ Represents a Hiven User Typing in a room """
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
    async def create_from_dict(cls, data: dict, client, *, user, room, house: typing.Optional[HivenObject] = None):
        """
        Creates an instance of the Relationship Class with the passed data

        ---

        Represent typing event and therefore needs its attribute passed to be used

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :param user: The user that is typing
        :param room: The room where the user is typing
        :param house: The house where the user is typing [Optional]
        :return: The newly constructed Relationship Instance
        """
        try:
            data['author'] = user
            data['house'] = house
            data['room'] = room

            timestamp = data.get('timestamp')
            # Converting to seconds because it's in milliseconds
            if utils.convertible(int, timestamp):
                data['timestamp'] = datetime.datetime.fromtimestamp(utils.convert_value(int, timestamp))
            else:
                data['timestamp'] = timestamp

            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            ) from e
        else:
            instance._client = client
            return instance

    @property
    def timestamp(self) -> datetime.datetime:
        return getattr(self, '_timestamp', None)

    @property
    def author(self):
        return getattr(self, '_author', None)

    @property
    def house(self):
        return getattr(self, '_house', None)

    @property
    def room(self):
        return getattr(self, '_room', None)

    @property
    def author_id(self):
        return getattr(self, '_author_id', None)

    @property
    def house_id(self):
        return getattr(self, '_house_id', None)

    @property
    def room_id(self):
        return getattr(self, '_room_id', None)
