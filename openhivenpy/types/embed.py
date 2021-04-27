# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
from typing import Optional
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

import fastjsonschema

from . import DataClassObject
from .. import utils
from ..exceptions import InitializationError

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Embed']


class Embed(DataClassObject):
    """ Represents an embed message object either customised or from a website """
    json_schema = {
        'type': 'object',
        'properties': {
            'url': {'type': 'string', 'default': None},
            'type': {'type': 'integer'},
            'title': {'type': 'string'},
            'image': {'type': 'string', 'default': None},
            'description': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            }
        },
        'additionalProperties': False,
        'required': ['type', 'title']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        """
        Represents an embed message object either customised or from a website

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        try:
            self._url = data.get('url')
            self._type = data.get('type')
            self._title = data.get('title')
            self._image = data.get('image')
            self._description = data.get('description')

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
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        return cls.validate(data)

    @property
    def url(self) -> Optional[str]:
        return getattr(self, '_url', None)
    
    @property
    def type(self) -> Optional[int]:
        return getattr(self, '_type', None)
    
    @property 
    def title(self) -> Optional[str]:
        return getattr(self, '_title', None)

    @property 
    def image(self) -> Optional[str]:
        return getattr(self, '_image', None)
    
    @property
    def description(self) -> Optional[str]:
        return getattr(self, '_description', None)
