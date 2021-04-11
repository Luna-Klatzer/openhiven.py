# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import typing
import fastjsonschema

from . import HivenTypeObject, check_valid
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import House
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Entity']


class Entity(HivenTypeObject):
    """ Represents a Hiven Entity inside a House which can contain Rooms """
    json_schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'name': {'type': 'string'},
            'type': {'type': 'integer', 'default': 1},
            'resource_pointers': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'},
                ],
                'default': []
            },
            'house_id': {'type': 'string'},
            'house': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'string'},
                    {'type': 'null'},
                ]
            },
            'position': {'type': 'integer'}
        },
        'additionalProperties': False,
        'required': ['id', 'name', 'position', 'resource_pointers', 'house_id']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        """
        Represents a Hiven Entity inside a House which can contain Rooms

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        try:
            super().__init__()
            self._type = data.get('type')
            self._position = data.get('position')
            self._resource_pointers = data.get('resource_pointers')
            self._name = data.get('name')
            self._id = data.get('id')
            self._house_id = data.get('house_id')
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
            self._client = client

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('position', self.position),
            ('type', self.type)
        ]
        return '<Entity {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Optional[dict]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['entities'].get(self.id)

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

        data['house'] = data['house_id']
        data = cls.validate(data)
        return data

    @property
    def type(self) -> int:
        return getattr(self, '_type', None)

    @property
    def resource_pointers(self) -> list:
        return getattr(self, '_resource_pointers', None)

    @property
    def name(self) -> str:
        return getattr(self, '_name', None)

    @property
    def id(self) -> str:
        return getattr(self, '_id', None)

    @property
    def house_id(self) -> str:
        return getattr(self, '_house_id', None)

    @property
    def position(self) -> int:
        return getattr(self, '_position', None)

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
            self._house = House(
                data=self._client.storage['house'][house_id], client=self._client
            )
            return self._house
        elif type(self._house) is House:
            return self._house
        else:
            return None
