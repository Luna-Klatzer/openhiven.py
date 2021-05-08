# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
from typing import Optional, Union
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

import fastjsonschema

from . import DataClassObject
from ..exceptions import InitializationError

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['LazyUser', 'User']


class LazyUser(DataClassObject):
    """ Represents the standard Hiven User """
    json_schema = {
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'name': {'type': 'string'},
            'id': {'type': 'string'},
            'user_flags': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'bio': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'email_verified': {
                'anyOf': [
                    {'type': 'boolean'},
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
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            self._username = data.get('username')
            self._name = data.get('name')
            self._bio = data.get('bio')
            self._id = data.get('id')
            self._email_verified = data.get('email_verified')
            self._user_flags = data.get('user_flags')  # ToDo: Discord.py-esque way of user flags
            self._icon = data.get('icon')
            self._header = data.get('header')
            self._bot = data.get('bot', False)

        except Exception as e:
            raise InitializationError(f"Failed to initialise {self.__class__.__name__}") from e
        else:
            self._client = client

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
    def raw(self) -> Optional[dict]:
        return self._client.storage['users'][self.id]

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        data = cls.validate(data)
        return data

    @property
    def username(self) -> Optional[str]:
        return getattr(self, '_username', None)

    @property
    def name(self) -> Optional[str]:
        return getattr(self, '_name', None)

    @property
    def id(self) -> Optional[str]:
        return getattr(self, '_id', None)

    @property
    def bio(self) -> Optional[str]:
        return getattr(self, '_bio', None)

    @property
    def email_verified(self) -> Optional[bool]:
        return getattr(self, '_email_verified', None)

    @property
    def user_flags(self) -> Optional[Union[int, str]]:
        return getattr(self, '_user_flags', None)

    @property
    def icon(self) -> Optional[str]:
        if getattr(self, '_icon', None):
            return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"
        else:
            return None

    @property
    def header(self) -> Optional[str]:
        if getattr(self, '_header', None):
            return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
        else:
            return None

    @property
    def bot(self) -> Optional[bool]:
        return getattr(self, '_bot', None)


class User(LazyUser):
    """ Represents the regular extended Hiven User """
    json_schema = {
        'type': 'object',
        'properties': {
            **LazyUser.json_schema['properties'],
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
        'required': [*LazyUser.json_schema['required']]
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            super().__init__(data, client)
            self._location = data.get('location')
            self._website = data.get('website')
            self._blocked = data.get('blocked')
            self._presence = data.get('presence')
            self._email = data.get('email')
            self._mfa_enabled = data.get('mfa_enabled')

        except Exception as e:
            raise InitializationError(f"Failed to initialise {self.__class__.__name__}") from e

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
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        data = LazyUser.format_obj_data(data)
        data = cls.validate(data)
        return data

    def get_cached_data(self) -> Optional[dict]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['users'][self.id]

    @property
    def location(self) -> Optional[str]:
        return getattr(self, '_location', None)

    @property
    def website(self) -> Optional[str]:
        return getattr(self, '_website', None)

    @property
    def presence(self) -> Optional[str]:
        return getattr(self, '_presence', None)

    @property
    def email(self) -> Optional[str]:
        return getattr(self, '_email', None)

    @property
    def blocked(self) -> Optional[bool]:
        return getattr(self, '_blocked', None)

    @property
    def mfa_enabled(self) -> Optional[bool]:
        return getattr(self, '_mfa_enabled', None)
