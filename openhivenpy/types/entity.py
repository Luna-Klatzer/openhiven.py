import logging
import sys
import types
import typing

import fastjsonschema

from . import HivenObject, check_valid
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Entity']


class Entity(HivenObject):
    """
    Represents a Hiven Entity
    """
    schema = {
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
            'position': {'type': 'integer'}
        },
        'additionalProperties': False,
        'required': ['id', 'name', 'position', 'resource_pointers']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._type = kwargs.get('type')
        self._position = kwargs.get('position')
        self._resource_pointers = kwargs.get('resource_pointers')
        self._name = kwargs.get('name')
        self._id = kwargs.get('id')
        self._house_id = kwargs.get('house_id')
        self._house = kwargs.get('house')

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('position', self.position),
            ('type', self.type)
        ]
        return '<Entity {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Union[dict, None]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['entities'][self.id]

    @classmethod
    @check_valid()
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        if data.get('house_id') is None and data.get('house'):
            house = data.pop('house')
            if type(house) is dict:
                house_id = house.get('id')
            elif isinstance(house, HivenObject):
                house_id = getattr(house, 'id')
            else:
                raise InvalidPassedDataError("Missing house_id field in data", data)
            data['house_id'] = house_id

        data = cls.validate(data)
        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the Entity Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Embed Instance
        """
        try:
            from . import House
            data['house'] = House.create_from_dict(client.storage['house'][data['house_id']])
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
    def type(self) -> int:
        return getattr(self, '_type', None)

    @property
    def resource_pointers(self) -> list:
        return getattr(self, '_resource_pointers', None)

    @property
    def name(self) -> list:
        return getattr(self, '_name', None)

    @property
    def id(self) -> list:
        return getattr(self, '_id', None)

    @property
    def house_id(self) -> list:
        return getattr(self, '_house_id', None)

    @property
    def position(self) -> int:
        return getattr(self, '_position', None)

    @property
    def house(self) -> int:
        return getattr(self, '_house', None)
