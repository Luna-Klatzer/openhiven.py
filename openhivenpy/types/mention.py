"""
Mention File which implements the Hiven Mention type

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

from .hiven_type_schemas import MentionSchema, get_compiled_validator
from .user import User
from .. import utils
from ..base_types import DataClassObject
from ..exceptions import InvalidPassedDataError
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Mention']


class Mention(DataClassObject):
    """ Represents an mention for a user in Hiven """
    _json_schema: dict = MentionSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('Mention')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._timestamp = data.get('timestamp')
        self._user = data.get('user')
        self._user_id = data.get('user_id')
        self._author = data.get('author')
        self._author_id = data.get('author_id')
        self._client = client

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be 
        required for the creation of an instance.


        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a 
         new class instance
        """
        if not data.get('user_id') and data.get('user'):
            user = data.pop('user')
            if type(user) is dict:
                user = user.get('id', None)
            elif isinstance(user, DataClassObject):
                user = getattr(user, 'id', None)
            else:
                user = None

            if user is None:
                raise InvalidPassedDataError("The passed user is not in the correct format!", data=data)
            else:
                data['user'] = user

        if not data.get('author_id') and data.get('author'):
            author = data.pop('author')
            if type(author) is dict:
                author = author.get('id', None)
            elif isinstance(author, DataClassObject):
                author = getattr(author, 'id', None)
            else:
                author = None

            if author is None:
                raise InvalidPassedDataError("The passed author is not in the correct format!", data=data)
            else:
                data['author'] = author

        data['author'] = data.get('author_id')
        data['user'] = data.get('user_id')
        data = cls.validate(data)
        return data

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
    def user(self) -> Optional[User]:
        if type(self._user) is str:
            user_id = self._user
        elif type(self.user_id) is str:
            user_id = self.user_id
        else:
            user_id = None

        if type(user_id) is str:
            data = self._client.storage['users'].get(user_id)
            if data:
                self._user = User(data=data, client=self._client)
                return self._user
            else:
                return None

        elif type(self._user) is User:
            return self._user
        else:
            return None

    @property
    def user_id(self) -> Optional[str]:
        return getattr(self, '_user_id', None)

    @property
    def author(self) -> Optional[User]:
        if type(self._author) is str:
            author_id = self._author
        elif type(self.author_id) is str:
            author_id = self.author_id
        else:
            author_id = None

        if type(author_id) is str:
            data = self._client.storage['users'].get(author_id)
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
    def author_id(self) -> Optional[str]:
        return getattr(self, '_author_id', None)
