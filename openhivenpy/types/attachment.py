import logging
import sys
import types

import fastjsonschema

from . import HivenObject
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError

logger = logging.getLogger(__name__)

__all__ = ['Attachment']


class Attachment(HivenObject):
    """
    Represents a Hiven Attachment
    """
    schema = {
        'type': 'object',
        'properties': {
            'filename': {'type': 'string'},
            'media_url': {'type': 'string'},
            'raw': {
                'type': 'object',
                'default': {}
            },
        },
        'required': ['filename', 'media_url']
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
        """
        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._filename = kwargs.get('filename')
        self._media_url = kwargs.get('media_url')
        self._raw = kwargs.get('raw')

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
        data['raw'] = {**data, **data.get('raw', {})}
        return cls.validate(data)

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the Attachment Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Attachment Instance
        """
        try:
            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def filename(self):
        return getattr(self, '_filename', None)

    @property
    def media_url(self):
        return getattr(self, '_media_url', None)
    
    @property
    def raw(self):
        # Different files have different attribs
        return getattr(self, '_raw', None)
