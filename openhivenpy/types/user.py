import sys
import logging
import types
import typing

import fastjsonschema

from . import HivenObject
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['LazyUser', 'User']


class LazyUser(HivenObject):
    """
    Represents the standard Hiven User
    """
    schema = {
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'name': {'type': 'string'},
            'id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'}
                ],
            },
            'user_flags': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'header': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'icon': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'bot': {
                'anyOf': [
                    {'type': 'boolean'},
                    {'type': 'string'},  # TODO! Needs to be removed when the string bug disappeared
                    {'type': 'null'}
                ],
                'default': False
            }
        },
        'required': ['username', 'name', 'id']
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
        self._username = kwargs.get('username')
        self._name = kwargs.get('name')
        self._id = kwargs.get('id')
        self._user_flags = kwargs.get('user_flags')  # ToDo: Discord.py-esque way of user flags
        self._icon = kwargs.get('icon')
        self._header = kwargs.get('header')
        self._bot = kwargs.get('bot', False)

    def __repr__(self) -> str:
        info = [
            ('username', self.username),
            ('name', self.name),
            ('id', self.id),
            ('icon', self.icon),
            ('header', self.header),
            ('bot', self.bot)
        ]
        return '<LazyUser {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def raw(self) -> typing.Union[dict, None]:
        if getattr(self, '_client') is not None:
            return self._client.storage['users'][self.id]
        else:
            return None

    @classmethod
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data['id'] = int(data['id'])
        data['owner_id'] = int(data['id'])
        return data

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the LazyUser Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed LazyUser Instance
        """
        try:
            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def username(self) -> str:
        return getattr(self, '_username', None)

    @property
    def name(self) -> str:
        return getattr(self, '_name', None)

    @property
    def id(self) -> int:
        return getattr(self, '_id', None)

    @property
    def user_flags(self) -> typing.Union[int, str]:
        return getattr(self, '_user_flags', None)

    @property
    def icon(self) -> typing.Union[str, None]:
        if getattr(self, '_icon', None):
            return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"
        else:
            return None

    @property
    def header(self) -> typing.Union[str, None]:
        if getattr(self, '_header', None):
            return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
        else:
            return None
    
    @property
    def bot(self) -> bool:
        return getattr(self, '_bot', None)


class User(LazyUser):
    """
    Represents the regular extended Hiven User
    """
    schema = {
        'type': 'object',
        'properties': {
            **LazyUser.schema['properties'],
            'location': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'website': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'presence': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'email': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'blocked': {
                'anyOf': [
                    {'type': 'boolean'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'mfa_enabled': {
                'anyOf': [
                    {'type': 'boolean'},
                    {'type': 'null'}
                ],
                'default': None
            },
        },
        'additionalProperties': False,
        'required': [*LazyUser.schema['required']]
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
        super().__init__(**kwargs)
        self._location = kwargs.get('location')
        self._website = kwargs.get('website')
        self._blocked = kwargs.get('blocked')
        self._presence = kwargs.get('presence')
        self._email = kwargs.get('email')
        self._mfa_enabled = kwargs.get('mfa_enabled')

    def __repr__(self) -> str:
        info = [
            ('username', self.username),
            ('name', self.name),
            ('id', self.id),
            ('icon', self.icon),
            ('header', self.header),
            ('bot', self.bot)
        ]
        return '<User {}>'.format(' '.join('%s=%s' % t for t in info))

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
        data = LazyUser.validate(data)
        return data

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the User Class with the passed data

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed User Instance
        """
        try:
            data['id'] = utils.convert_value(int, data.get('id'))

            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def location(self) -> str:
        return getattr(self, '_location', None)

    @property
    def website(self) -> str:
        return getattr(self, '_website', None)

    @property
    def presence(self):
        return getattr(self, '_presence', None)

    @property
    def email(self):
        return getattr(self, '_email', None)

    @property
    def blocked(self):
        return getattr(self, '_blocked', None)

    @property
    def mfa_enabled(self):
        return getattr(self, '_mfa_enabled', None)
