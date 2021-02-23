import logging
import sys
import types
import fastjsonschema

from .. import utils
from . import HivenObject
from ..exceptions import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Context']


class Context(HivenObject):
    """
    Represents a Command Context for a triggered command in the CommandListener
    """
    schema = {
        'type': 'object',
        'properties': {
            'room': {'type': 'object'},
            'author': {'type': 'object'},
            'created_at': {'type': 'string'},
            'house': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ]
            },
        },
        'additionalProperties': False,
        'required': ['room', 'author', 'created_at']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    @classmethod
    def validate(cls, data, *args, **kwargs):
        try:
            return cls.json_validator(data, *args, **kwargs)
        except Exception as e:
            utils.log_validation_traceback(cls, data, e)
            raise

    def __init__(self, **kwargs):
        """
        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._room = kwargs.get('room')
        self._author = kwargs.get('author')
        self._house = kwargs.get('house')
        self._created_at = kwargs.get('created_at')

    @classmethod
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        room = data['room']
        if room:
            if type(room) is dict:
                room = room.get('id')
            elif isinstance(room, HivenObject):
                room = getattr(room, 'id')
            data['room'] = int(room)

        house = data['house']
        if house:
            if type(house) is dict:
                house = house.get('id')
            elif isinstance(house, HivenObject):
                house = getattr(house, 'id')
            data['house'] = int(house)
        return data

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the Context Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Context Instance
        """
        try:
            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def house(self):
        return getattr(self, '_house', None)

    @property
    def author(self):
        return getattr(self, '_author', None)

    @property
    def room(self):
        return getattr(self, '_room', None)

    @property
    def created_at(self):
        return getattr(self, '_created_at', None)
