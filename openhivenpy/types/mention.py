import logging
import datetime
import sys
import types
import typing
import fastjsonschema

from .. import utils
from . import HivenObject, check_valid
from . import user
from ..exceptions import InvalidPassedDataError, InitializationError
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
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the Mention Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Mention Instance
        """
        try:
            data['user'] = user.User.create_from_dict(client.storage['users'][data['user']['id']], client)
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
    def timestamp(self):
        return self._timestamp
    
    @property
    def user(self):
        return self._user
    
    @property
    def author(self):
        return self._author
