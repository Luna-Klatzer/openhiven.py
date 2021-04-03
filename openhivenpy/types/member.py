import logging
import sys
import types
import typing
import fastjsonschema

from . import HivenObject, check_valid
from . import user
from .. import utils
from ..exceptions import InitializationError, HTTPForbiddenError

logger = logging.getLogger(__name__)

__all__ = ['Member']


class Member(user.User):
    """
    Represents a House Member on Hiven
    """
    schema = {
        'type': 'object',
        'properties': {
            **user.User.schema['properties'],
            'user_id': {'type': 'string'},
            'house_id': {'type': 'string'},
            'joined_at': {'type': 'string'},
            'roles': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'}
                ],
                'default': {},
            }
        },
        'additionalProperties': False,
        'required': [*user.User.schema['required'], 'user_id', 'house_id', 'joined_at']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._user_id = kwargs.get('user_id')
        self._house_id = kwargs.get('house_id')
        self._joined_at = kwargs.get('joined_at')
        self._roles = kwargs.get('roles')
        self._house = kwargs.get('house')
        super().__init__(**kwargs.get('user'))

    def __repr__(self) -> str:
        info = [
            ('username', self.username),
            ('name', self.name),
            ('id', self.id),
            ('icon', self.icon),
            ('header', self.header),
            ('bot', self.bot),
            ('house_id', self.house_id),
            ('joined_house_at', self.joined_house_at)
        ]
        return '<Member {}>'.format(' '.join('%s=%s' % t for t in info))

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

        if type(data.get('house_id')):
            data['house_id'] = data.get('house_id')
        else:
            data['house_id'] = getattr(data['house'], 'id')
        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the Member Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Member Instance
        """
        try:
            data = {**data.get('user'), **data}
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
    def id(self) -> str:
        return getattr(self, '_user_id', None)

    @property
    def user_id(self) -> str:
        return getattr(self, '_user_id', None)

    @property
    def joined_house_at(self) -> str:
        return getattr(self, '_joined_at', None)

    @property
    def house_id(self) -> str:
        return getattr(self, '_house_id', None)

    @property
    def roles(self) -> typing.List[HivenObject]:
        return getattr(self, '_roles', None)

    @property
    def joined_at(self) -> str:
        return getattr(self, '_joined_at', None)

    async def kick(self) -> bool:
        """
        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise `HivenException.Forbidden`
            
        :return: True if the request was successful else HivenException.Forbidden()
        """
        resp = await self._client.http.delete(f"/{self._house_id}/members/{self._user_id}")
        if not resp.status < 300:
            raise HTTPForbiddenError()
        else:
            return True
