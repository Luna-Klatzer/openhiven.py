# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import typing
import fastjsonschema

from .. import utils
from . import HivenTypeObject, check_valid
from ..exceptions import InvalidPassedDataError, InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import House, User, Room
    from .. import HivenClient


logger = logging.getLogger(__name__)

__all__ = ['Context']


class Context(HivenTypeObject):
    """ Represents a Command Context for a triggered command that was registered prior """
    json_schema = {
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
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        """
        Represents a Command Context for a triggered command that was registered prior

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        try:
            self._room = data.get('room')
            self._author = data.get('author')
            self._house = data.get('house')
            self._created_at = data.get('created_at')

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
        data = cls.validate(data)

        if not data.get('room_id') and data.get('room'):
            room = data.pop('room')
            if type(room) is dict:
                room = room.get('id', None)
            elif isinstance(room, HivenTypeObject):
                room = getattr(room, 'id', None)
            else:
                room = None

            if room is None:
                raise InvalidPassedDataError("The passed room is not in the correct format!", data=data)
            else:
                data['room_id'] = room

        if not data.get('house_id') and data.get('house'):
            house = data.pop('house')
            if type(house) is dict:
                house = house.get('id', None)
            elif isinstance(house, HivenTypeObject):
                house = getattr(house, 'id', None)
            else:
                house = None

            if house is None:
                raise InvalidPassedDataError("The passed house is not in the correct format!", data=data)
            else:
                data['house_id'] = house

        data['room'] = data['room_id']
        data['house'] = data['house_id']
        return data

    @property
    def house(self) -> typing.Optional[House]:
        from . import House
        if type(self._house) is str:
            data = self._client.storage['houses'][self._house]
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
    def room(self) -> typing.Optional[Room]:
        from . import Room
        if type(self._room) is str:
            data = self._client.storage['rooms']['house'].get(self._room)
            if data:
                self._room = Room(data=data, client=self._client)
                return self._room
            else:
                return None

        elif type(self._room) is Room:
            return self._room
        else:
            return None

    @property
    def author(self) -> typing.Optional[User]:
        from . import User
        if type(self._author) is str:
            data = self._client.storage['users'][self._author]
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
    def created_at(self) -> str:
        return getattr(self, '_created_at', None)
