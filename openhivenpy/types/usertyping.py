"""
UserTyping File which implements the UserTyping
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

import datetime
import logging
from typing import Optional
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from . import House, TextRoom, User
from .. import utils
from ..base_types import DataClassObject
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['UserTyping']


class UserTyping(DataClassObject):
    """ Represents a Hiven User typing in a room """

    @log_type_exception('UserTyping')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._author = data.get('author')
        self._room = data.get('room')
        self._house = data.get('house')
        self._author_id = data.get('author_id')
        self._house_id = data.get('house_id')
        self._room_id = data.get('room_id')
        self._timestamp = data.get('timestamp')
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
        """ Time-stamp of the User-Typing (unix) """
        if utils.convertible(int, self._timestamp):
            # Converting to seconds because it's in milliseconds
            self._timestamp = datetime.datetime.fromtimestamp(
                utils.safe_convert(int, self._timestamp) / 1000
            )
            return self._timestamp
        elif type(self._timestamp) is datetime.datetime:
            return self._timestamp
        else:
            return None

    @property
    def author(self) -> Optional[User]:
        """ Author object of the User-Typing Class """
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
        """ House object of the Context Class """
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
        """ Room object of the Context Class """
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
        """ ID of the parent Author object of the Context Class """
        return getattr(self, '_author_id', None)

    @property
    def house_id(self) -> Optional[str]:
        """ ID of the parent House object of the Context Class """
        return getattr(self, '_house_id', None)

    @property
    def is_house_typing(self) -> bool:
        """ Returns whether the typing is inside a house """
        return self.house_id is not None

    @property
    def room_id(self) -> Optional[str]:
        """ ID of the parent Room object of the Context Class """
        return getattr(self, '_room_id', None)
