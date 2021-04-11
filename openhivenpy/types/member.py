# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import typing
import fastjsonschema

from . import HivenTypeObject, check_valid
from . import user
from .. import utils
from ..exceptions import InitializationError, HTTPForbiddenError, InvalidPassedDataError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import HivenClient
    from . import House

logger = logging.getLogger(__name__)

__all__ = ['Member']


class Member(user.User):
    """ Represents a House Member on Hiven which contains the Hiven User, role-data and member-data """
    json_schema = {
        'type': 'object',
        'properties': {
            **user.User.json_schema['properties'],
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
        'required': [*user.User.json_schema['required'], 'user_id', 'house_id', 'joined_at']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        super().__init__(**data.get('user'))
        try:
            data = {**data.get('user'), **data}
            self._user_id = data.get('user_id')
            self._house_id = data.get('house_id')
            self._joined_at = data.get('joined_at')
            self._roles = data.get('roles')
            self._house = data.get('house')

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
            data._client = client

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

        if not data.get('house_id') and data.get('house'):
            house = data.pop('house')
            if type(house) is dict:
                house_id = house.get('id')
            elif isinstance(house, HivenTypeObject):
                house_id = getattr(house, 'id', None)
            else:
                house_id = None

            if house_id is None:
                raise InvalidPassedDataError("The passed house is not in the correct format!", data=data)
            else:
                data['house_id'] = house_id
        else:
            raise InvalidPassedDataError("house_id and house missing from required data", data=data)
        data['house'] = data['house_id']
        return data

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
    def house(self) -> typing.Optional[House]:
        from . import House
        if type(self._house) is str:
            house_id = self._house
        elif type(self.house_id) is str:
            house_id = self.house_id
        else:
            house_id = None

        if house_id:
            data = self._client.storage['houses'][house_id]
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
    def house_id(self) -> str:
        return getattr(self, '_house_id', None)

    @property
    def roles(self) -> typing.List[dict]:
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
        try:
            resp = await self._client.http.delete(f"/{self._house_id}/members/{self._user_id}")
            if not resp.status < 300:
                raise HTTPForbiddenError()
            else:
                return True
        except HTTPForbiddenError:
            raise

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to kick the member due to an exception occurring: \n{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return False
