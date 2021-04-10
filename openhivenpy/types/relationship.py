import logging
import sys
import types
import typing
import fastjsonschema

from . import HivenObject, check_valid
from . import User
from .. import utils
from ..exceptions import InitializationError

logger = logging.getLogger(__name__)

__all__ = ['Relationship']


class Relationship(HivenObject):
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
    schema = {
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
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._user_id = kwargs.get('user_id')
        self._user = kwargs.get('user')
        self._type = kwargs.get('type')
        self._last_updated_at = kwargs.get('last_updated_at')

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('user_id', self.user_id),
            ('user', repr(self.user)),
            ('type', self.type)
        ]
        return '<Relationship {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Union[dict, None]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['relationships'][self.user_id]

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data['type'] = data.get('type')
        data['user_id'] = data.get('user_id')
        data['user'] = data.pop('user')['id']
        return data

    @classmethod
    def _insert_data(cls, data: dict, client):
        """
        Creates an instance of the Relationship Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Relationship Instance
        """
        try:
            data['user_id'] = data.get('user_id')
            user_data = client.storage['users'][data['user_id']]
            data['user'] = User._insert_data(user_data, client)

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
    def user(self) -> User:
        return getattr(self, '_user', None)

    @property
    def type(self) -> int:
        return getattr(self, '_type', None)

    @property
    def user_id(self) -> str:
        return getattr(self, '_user_id', None)

    @property
    def id(self) -> str:
        return getattr(self, '_id', None)
