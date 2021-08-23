# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import datetime
import logging
from typing import Optional
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from . import House, TextRoom, User
from .. import utils
from ..base_types import DataClassObject
from ..exceptions import InitializationError

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['UserTyping']


class UserTyping(DataClassObject):
    """ Represents a Hiven User typing in a room """

    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        try:
            self._author = data.get('author')
            self._room = data.get('room')
            self._house = data.get('house')
            self._author_id = data.get('author_id')
            self._house_id = data.get('house_id')
            self._room_id = data.get('room_id')
            self._timestamp = data.get('timestamp')

        except Exception as e:
            raise InitializationError(
                f"Failed to initialise {self.__class__.__name__}"
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
    def timestamp(self) -> Optional[datetime.datetime]:
        if utils.convertible(int, self._timestamp):
            # Converting to seconds because it's in milliseconds
            self._timestamp = datetime.datetime.fromtimestamp(utils.safe_convert(int, self._timestamp) / 1000)
            return self._timestamp
        elif type(self._timestamp) is datetime.datetime:
            return self._timestamp
        else:
            return None

    @property
    def author(self) -> Optional[User]:
        if type(self._author) is str:
            data = self._client.storage['users'].get(self._author)
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
    def house(self) -> Optional[House]:
        if type(self._house) is str:
            data = self._client.storage['houses'].get(self._house)
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
    def room(self) -> Optional[TextRoom]:
        if type(self._room) is str:
            data = self._client.storage['rooms']['house'].get(self._room)
            if data:
                self._room = TextRoom(data=data, client=self._client)
                return self._room
            else:
                return None

        elif type(self._room) is TextRoom:
            return self._room
        else:
            return None

    @property
    def author_id(self) -> Optional[str]:
        return getattr(self, '_author_id', None)

    @property
    def house_id(self) -> Optional[str]:
        return getattr(self, '_house_id', None)

    @property
    def room_id(self) -> Optional[str]:
        return getattr(self, '_room_id', None)
