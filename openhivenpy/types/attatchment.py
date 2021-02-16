import logging
import sys
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from . import HivenObject
from .. import utils
from .. import exception as errs

logger = logging.getLogger(__name__)

__all__ = ('Attachment', 'AttachmentSchema')


class AttachmentSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    filename = fields.Str(required=True)
    media_url = fields.Str(required=True)
    raw = fields.Dict(required=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns the class Attachment using the @classmethod inside the Class to correctly initialise the object
        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Attachment Object
        """
        return Attachment(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = AttachmentSchema()


class Attachment(HivenObject):
    """
    Represents a Hiven Attachment
    """
    def __init__(self, **kwargs):
        """
        Object Instance Construction

        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._filename = kwargs.get('filename')
        self._media_url = kwargs.get('media_url')
        self._raw = kwargs.get('raw')

    @classmethod
    async def from_dict(cls, data: dict, http, **kwargs):
        """
        Creates an instance of the Attachment Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed Attachment Instance
        """
        try:
            data['raw'] = dict(data)  # Adding the raw field

            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise errs.InvalidPassedDataError(data=data)

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise errs.InitializationError(f"Failed to initialise {cls.__name__} due to exception:\n"
                                           f"{sys.exc_info()[0].__name__}: {e}!")
        else:
            # Adding the http attribute for API interaction
            instance._http = http

            return instance

    @property
    def filename(self):
        return self._filename

    @property
    def media_url(self):
        return self._media_url
    
    @property
    def raw(self):
        # Different files have different attribs
        return self._raw
