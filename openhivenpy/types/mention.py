# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import datetime
import logging
import sys
from typing import Optional
import fastjsonschema

from . import HivenTypeObject, check_valid
from . import User
from .. import utils
from ..exceptions import InitializationError, InvalidPassedDataError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Mention']


class Mention(HivenTypeObject):
    """ Represents an mention for a user in Hiven """
    json_schema = {
        'type': 'object',
        'properties': {
            'timestamp': {'type': 'string'},
            'user': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
            },
            'author': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
            },
        },
        'additionalProperties': False,
        'required': ['timestamp', 'user', 'author']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            self._timestamp = data.get('timestamp')
            self._user = data.get('user')
            self._user_id = data.get('user_id')
            self._author = data.get('author')
            self._author_id = data.get('author_id')

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

    @classmethod
    @check_valid
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        if not data.get('user_id') and data.get('user'):
            user = data.pop('user')
            if type(user) is dict:
                user = user.get('id', None)
            elif isinstance(user, HivenTypeObject):
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
            elif isinstance(author, HivenTypeObject):
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
