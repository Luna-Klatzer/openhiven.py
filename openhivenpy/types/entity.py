import logging
import sys
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from . import HivenObject
from .. import utils
from ..exception import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Entity', 'EntitySchema']


class EntitySchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    id = fields.Int(required=True)
    name = fields.Str(required=True)
    type = fields.Int(required=True)
    resource_pointers = fields.List(fields.Field(), required=True)
    house_id = fields.Str(default=None)
    position = fields.Int(default=0)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Entity Object
        """
        return Entity(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = EntitySchema()


class Entity(HivenObject):
    """
    Represents a Hiven Entity
    """
    _http = None

    def __init__(self, **kwargs):
        self._type = kwargs.get('type', 1)
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

    @classmethod
    async def from_dict(cls, data: dict, http, house, **kwargs):
        """
        Creates an instance of the Entity Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param house: House of the Entity
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed Embed Instance
        """
        try:
            data['id'] = utils.convert_value(int, data.get('id'))
            data['house'] = house

            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise InvalidPassedDataError(data=data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(f"Failed to initialise {cls.__name__} due to exception:\n"
                                      f"{sys.exc_info()[0].__name__}: {e}!")
        else:
            # Adding the http attribute for API interaction
            instance._http = http

            return instance

    @property
    def type(self) -> int:
        return self._type

    @property
    def resource_pointers(self) -> list:
        return self._resource_pointers

    @property
    def name(self) -> list:
        return self._name

    @property
    def id(self) -> list:
        return self._id

    @property
    def house_id(self) -> list:
        return self._house_id

    @property
    def position(self) -> int:
        return self._position

    @property
    def house(self) -> int:
        return self._house
