import sys
import logging
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from . import HivenObject
from .. import utils

logger = logging.getLogger(__name__)

__all__ = ('LazyUser', 'User', 'LazyUserSchema')


class LazyUserSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    id = fields.Int(required=True)
    name = fields.Str(required=True)
    username = fields.Str(required=True, allow_none=True)
    user_flags = fields.Raw(default=None, allow_none=True)
    icon = fields.Str(default=None, allow_none=True)
    header = fields.Str(default=None, allow_none=True)
    bot = fields.Bool(default=False, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new LazyUser Object
        """
        return LazyUser(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_LAZY_SCHEMA = LazyUserSchema()


class UserSchema(LazyUserSchema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    location = fields.Str(default=None, allow_none=True)
    website = fields.Str(default=None, allow_none=True)
    presence = fields.Str(default=None, allow_none=True)
    bio = fields.Str(default=None, allow_none=True)
    blocked = fields.Bool(default=False, allow_none=True)
    email_verified = fields.Bool()
    email = fields.Str(default=None, allow_none=True)
    mfa_enabled = fields.Bool(default=None, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new User Object
        """
        return User(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = UserSchema()


class LazyUser(HivenObject):
    """
    Represents the standard Hiven User
    """
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

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        http,
                        **kwargs):
        """
        Creates an instance of the LazyUser Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :return: The newly constructed LazyUser Instance
        """
        try:
            if data.get('user') is not None:
                data = data.get('user')
            data['id'] = utils.convert_value(int, data.get('id'))

            instance = GLOBAL_LAZY_SCHEMA.load(data, unknown=EXCLUDE)
            # Adding the http attribute for API interaction
            instance._http = http
            return instance

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            return None

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")

    @property
    def username(self) -> str:
        return self._username

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def icon(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
    
    @property
    def bot(self) -> bool:
        return self._bot


class User(LazyUser):
    """
    Represents the regular extended Hiven User
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._location = kwargs.get('location')
        self._website = kwargs.get('website')
        self._presence = kwargs.get('presence')  # ToDo: Replace with classic presence string
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
    async def from_dict(cls,
                        data: dict,
                        http,
                        **kwargs):
        """
        Creates an instance of the User Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :return: The newly constructed User Instance
        """
        try:
            if data.get('user') is not None:
                data = data.get('user')
            data['id'] = utils.convert_value(int, data.get('id'))

            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)
            # Adding the http attribute for API interaction
            instance._http = http
            return instance

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            return None

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")

    @property
    def location(self) -> str:
        return self._location

    @property
    def website(self) -> str:
        return self._website

    # Still needs to be worked out
    @property
    def presence(self):
        return self._presence
