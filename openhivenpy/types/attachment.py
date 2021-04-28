# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

import fastjsonschema

from . import DataClassObject
from .. import utils
from ..exceptions import InitializationError

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Attachment']


class Attachment(DataClassObject):
    """ Represents a Hiven Message Attachment containing a file """
    json_schema = {
        'type': 'object',
        'properties': {
            'filename': {'type': 'string'},
            'media_url': {'type': 'string'},
            'raw': {
                'type': 'object',
                'default': {}
            },
        },
        'additionalProperties': False,
        'required': ['filename', 'media_url']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        """
        Represents a Hiven Message Attachment containing a file

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        try:
            self._filename = data.get('filename')
            self._media_url = data.get('media_url')
            self._raw = data.get('raw')

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
        data['raw'] = {**data.pop('raw', {}), **data}
        return cls.validate(data)

    @property
    def filename(self) -> str:
        return getattr(self, '_filename', None)

    @property
    def media_url(self) -> str:
        return getattr(self, '_media_url', None)

    @property
    def raw(self) -> dict:
        # Different files have different attribs
        return getattr(self, '_raw', None)
