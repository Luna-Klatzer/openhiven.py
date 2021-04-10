import logging
import sys
import types
import typing
import fastjsonschema

from . import HivenObject, check_valid
from . import User
from .. import utils
from ..exceptions import InitializationError, InvalidPassedDataError

logger = logging.getLogger(__name__)

__all__ = ['Mention']


class Mention(HivenObject):
    """ Represents an mention for a user in Hiven """
    schema = {
        'type': 'object',
        'properties': {
            'timestamp': {'type': 'string'},
            'user': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
            },
            'author': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'null'}
                ],
            },
        },
        'additionalProperties': False,
        'required': ['timestamp', 'user', 'author']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._timestamp = kwargs.get('timestamp')
        self._user = kwargs.get('user')
        self._author = kwargs.get('author')

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
        user = data.get('user')
        if user:
            if type(user) is dict:
                user = user.get('id', None)
            elif isinstance(user, HivenObject):
                user = getattr(user, 'id', None)

            if user is None:
                raise InvalidPassedDataError("The passed house is not in the correct format!", data=data)
            else:
                data['user'] = user

        author = data.get('author')
        if author:
            if type(author) is dict:
                author = author.get('id', None)
            elif isinstance(author, HivenObject):
                author = getattr(author, 'id', None)

            if author is None:
                raise InvalidPassedDataError("The passed house is not in the correct format!", data=data)
            else:
                data['author'] = author

        return data

    @classmethod
    def _insert_data(cls, data: dict, client):
        """
        Creates an instance of the Mention Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Mention Instance
        """
        try:
            user_data = client.storage['users'][data['user']]
            data['user'] = User._insert_data(user_data, client)

            user_data = client.storage['users'][data['user']]
            data['author'] = User._insert_data(user_data, client)
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

    # Unknown type
    @property
    def timestamp(self) -> typing.Any:
        return self._timestamp
    
    @property
    def user(self) -> User:
        return self._user
    
    @property
    def author(self):
        return self._author
