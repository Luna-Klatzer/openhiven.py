# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import types
import fastjsonschema

from .. import utils
from . import HivenObject, check_valid
from ..exceptions import InvalidPassedDataError, InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import House, User, Room

logger = logging.getLogger(__name__)

__all__ = ['Context']


class Context(HivenObject):
    """ Represents a Command Context for a triggered command that was registered prior """
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

    def __init__(self, **kwargs):
        """
        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._room = kwargs.get('room')
        self._author = kwargs.get('author')
        self._house = kwargs.get('house')
        self._created_at = kwargs.get('created_at')

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

        room = data.get('room')
        if room:
            if type(room) is dict:
                room = room.get('id', None)
            elif isinstance(room, HivenObject):
                room = getattr(room, 'id', None)

            if room is None:
                raise InvalidPassedDataError("The passed room is not in the correct format!", data=data)
            else:
                data['room'] = room

        house = data.get('house')
        if house:
            if type(house) is dict:
                house = house.get('id', None)
            elif isinstance(house, HivenObject):
                house = getattr(house, 'id', None)

            if house is None:
                raise InvalidPassedDataError("The passed house is not in the correct format!", data=data)
            else:
                data['house'] = house
        return data

    @classmethod
    def _insert_data(cls, data: dict, client):
        """
        Creates an instance of the Context Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

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
    def house(self) -> House:
        return getattr(self, '_house', None)

    @property
    def author(self) -> User:
        return getattr(self, '_author', None)

    @property
    def room(self) -> Room:
        return getattr(self, '_room', None)

    @property
    def created_at(self) -> str:
        return getattr(self, '_created_at', None)
