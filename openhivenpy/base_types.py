""" Base types of the module """
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import sys
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import HivenClient

__all__ = [
    "HivenObject",
    "DataClassObject"
]


class HivenObject(ABC):
    """
    Base Class for all Hiven Type Classes. Used to signalise it's a
    generic type without specification
    """
    ...


class DataClassObject(HivenObject):
    """
    Data-Class object for the types sub-module of openhivenpy
    """
    _client: HivenClient = None

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
