# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import datetime
import logging
import sys
import typing

from . import HivenTypeObject, House, Room, User
from .. import utils
from ..exceptions import InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['UserTyping']


class UserTyping(HivenTypeObject):
    """ Represents a Hiven User typing in a room """
    def __init__(self, data: dict, client: HivenClient):
        try:
            self._author = data.get('author')
            self._room = data.get('room')
            self._house = data.get('house')
            self._author_id = data.get('author_id')
            self._house_id = data.get('house_id')
            self._room_id = data.get('room_id')
            self._timestamp = data.get('timestamp')

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
            ('house_id', self.house_id),
            ('author_id', self.author_id),
            ('room_id', self.room_id),
            ('author', repr(self.author))
        ]
        return '<Typing {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def timestamp(self) -> typing.Optional[datetime.datetime]:
        if utils.convertible(int, self._timestamp):
            # Converting to seconds because it's in milliseconds
            self._timestamp = datetime.datetime.fromtimestamp(utils.safe_convert(int, self._timestamp) / 1000)
            return self._timestamp
        elif type(self._timestamp) is datetime.datetime:
            return self._timestamp
        else:
            return None

    @property
    def author(self) -> typing.Optional[User]:
        if type(self._author) is str:
            data = self._client.storage['users'][self._author]
            if data:
                self._author = User(data=data, client=self._client)
                return self._author
            else:
                return None

        elif type(self._author) is User:
            return self._author
        else:
            return None

    @property
    def house(self) -> typing.Optional[House]:
        if type(self._house) is str:
            data = self._client.storage['houses'][self._house]
            if data:
                self._house = House(data=data, client=self._client)
                return self._house
            else:
                return None

        elif type(self._house) is House:
            return self._house
        else:
            return None

    @property
    def room(self) -> typing.Optional[Room]:
        if type(self._room) is str:
            data = self._client.storage['rooms']['house'][self._room]
            if data:
                self._room = Room(data=data, client=self._client)
                return self._room
            else:
                return None

        elif type(self._room) is Room:
            return self._room
        else:
            return None

    @property
    def author_id(self) -> str:
        return getattr(self, '_author_id', None)

    @property
    def house_id(self) -> str:
        return getattr(self, '_house_id', None)

    @property
    def room_id(self) -> str:
        return getattr(self, '_room_id', None)
