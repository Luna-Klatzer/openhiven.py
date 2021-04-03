import logging
import sys
import types
import fastjsonschema

from . import HivenObject, check_valid
from .. import utils
from ..exceptions import InitializationError

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
        'additionalProperties': False,
        'required': ['filename', 'media_url']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        """
        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._filename = kwargs.get('filename')
        self._media_url = kwargs.get('media_url')
        self._raw = kwargs.get('raw')

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data['raw'] = {**data.pop('raw', {}), **data}
        return cls.validate(data)

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the Attachment Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

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
    def filename(self) -> str:
        return getattr(self, '_filename', None)

    @property
    def media_url(self) -> str:
        return getattr(self, '_media_url', None)
    
    @property
    def raw(self) -> dict:
        # Different files have different attribs
        return getattr(self, '_raw', None)
