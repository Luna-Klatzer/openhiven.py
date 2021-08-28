""" Base types of the module """
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from .client import HivenClient

__all__ = [
    "HivenObject",
    "DataClassObject",
    "BaseUser"
]


class HivenObject(ABC):
    """
    Abstract Base Class for all Hiven Type Classes. Used to signalise it's a
    generic type without specification
    """
    ...


class DataClassObject(HivenObject):
    """
    Data-Class object for the types sub-module of openhivenpy
    """
    _client: HivenClient = None

    def __init__(self):
        self._json_schema: Optional[dict] = None

    @classmethod
    def validate(cls, data, *args, **kwargs) -> dict:
        """ Validates the data using the local class json_validator """
        try:
            return getattr(cls, 'json_validator')(data, *args, **kwargs)
        except Exception:
            from . import utils
            utils.log_validation_traceback(cls, data, sys.exc_info())
            raise

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        # Automatically creating a list of tuples for all values
        info = [
            (attribute.replace('_', ''),
             value) if attribute != '_client' else None
            for attribute, value in self.__dict__.items()
        ]

        return '<{} {}>'.format(self.__class__.__name__, ' '.join(
            '%s=%s' % t if t is not None else '' for t in info))

    @property
    def json_schema(self) -> dict:
        """ Schema to validate the Data Class using json-validation """
        return self._json_schema


class BaseUser(DataClassObject):
    """ Base User for Hiven """

    @property
    @abstractmethod
    def username(self) -> Optional[str]:
        """ Username of the user """
        return getattr(self, '_username', None)

    @property
    @abstractmethod
    def name(self) -> Optional[str]:
        """ Name of the user """
        return getattr(self, '_name', None)

    @property
    @abstractmethod
    def id(self) -> Optional[str]:
        """ Unique string id of the user """
        return getattr(self, '_id', None)

    @property
    @abstractmethod
    def bio(self) -> Optional[str]:
        """ Bio of the user """
        return getattr(self, '_bio', None)

    @property
    @abstractmethod
    def email_verified(self) -> Optional[bool]:
        """ Returns True if the email is verified """
        return getattr(self, '_email_verified', None)

    @property
    @abstractmethod
    def flags(self) -> Optional[Union[int, str]]:
        """ User flags represented as an numeric value/str """
        return getattr(self, '_flags', None)

    @property
    @abstractmethod
    def user_flags(self) -> Optional[Union[int, str]]:
        """ Alias for flags """
        return self.flags

    @property
    @abstractmethod
    def icon(self) -> Optional[str]:
        """ The icon of the user as a link """
        if getattr(self, '_icon', None):
            return f"https://media.hiven.io/v1/users/" \
                   f"{getattr(self, '_id')}/icons/{getattr(self, '_icon')}"
        else:
            return None

    @property
    @abstractmethod
    def header(self) -> Optional[str]:
        """ The header of the user as a link """
        if getattr(self, '_header', ''):  # can not be empty or None
            return f"https://media.hiven.io/v1/users/" \
                   f"{getattr(self, '_id')}/headers/{getattr(self, '_header')}"
        else:
            return None

    @property
    @abstractmethod
    def bot(self) -> Optional[bool]:
        """ Returns true when the user is a bot """
        return getattr(self, '_bot', None)

    @property
    @abstractmethod
    def account(self) -> Optional[str]:
        """ Returns the account id/string. Currently client-limited """
        _ = getattr(self, '_account', None)
        return str(_) if type(_) is int else _

    @property
    @abstractmethod
    def application(self) -> Optional[bool]:
        """ Returns the application string passed. Currently client-limited """
        return getattr(self, '_application', None)
