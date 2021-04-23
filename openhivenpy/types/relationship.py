# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

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

__all__ = ['Relationship']


class Relationship(HivenTypeObject):
    """
    Represents a user-relationship with another user or bot

    ---

    Possible Types:
    
    0 - No Relationship
    
    1 - Outgoing Friend Request
    
    2 - Incoming Friend Request
    
    3 - Friend
    
    4 - Restricted User
    
    5 - Blocked User
    """
    json_schema = {
        'type': 'object',
        'properties': {
            'user_id': {'type': 'string'},
            'user': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'object'},
                    {'type': 'null'}
                ],
            },
            'type': {'type': 'integer'},
            'last_updated_at': {'type': 'string'}
        },
        'additionalProperties': False,
        'required': ['user_id', 'type']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            self._user_id = data.get('user_id')
            self._user = data.get('user')
            self._type = data.get('type')
            self._last_updated_at = data.get('last_updated_at')

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
            ('id', self.id),
            ('user_id', self.user_id),
            ('user', repr(self.user)),
            ('type', self.type)
        ]
        return '<Relationship {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> Optional[dict]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['relationships'][self.user_id]

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
        data = cls.validate(data)
        data['type'] = utils.safe_convert(int, data.get('type'))

        if not data.get('user_id') and data.get('user'):
            user = data.pop('user')
            if type(user) is dict:
                user_id = user.get('id')
            elif isinstance(user, HivenTypeObject):
                user_id = getattr(user, 'id', None)
            else:
                user_id = None

            if user_id is None:
                raise InvalidPassedDataError("The passed user is not in the correct format!", data=data)
            else:
                data['user_id'] = user_id
        elif not data.get('user_id') and not data.get('user'):
            raise InvalidPassedDataError("user_id and user missing from required data", data=data)

        data['user'] = data['user_id']
        return data

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
    def type(self) -> Optional[int]:
        return getattr(self, '_type', None)

    @property
    def user_id(self) -> Optional[str]:
        return getattr(self, '_user_id', None)

    @property
    def id(self) -> Optional[str]:
        return getattr(self, '_id', None)
