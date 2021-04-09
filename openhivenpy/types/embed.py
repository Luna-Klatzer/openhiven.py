import logging
import sys
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from .. import utils
from . import HivenObject
from .. import exception as errs

logger = logging.getLogger(__name__)

__all__ = ('Embed', 'EmbedSchema')


class EmbedSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    url = fields.Str(required=True)
    type = fields.Str(required=True)
    title = fields.Str(required=True)
    image = fields.Str(default=None)
    description = fields.Str(default=None)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Embed Object
        """
        return Embed(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = EmbedSchema()


class Embed(HivenObject):
    """
    Represents an embed message object
    """
    def __init__(self, **kwargs):
        """
        Object Instance Construction

        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._url = kwargs.get('url')
        self._type = kwargs.get('type')
        self._title = kwargs.get('title')
        self._image = kwargs.get('image', None)
        self._description = kwargs.get('description', None)

    @classmethod
    async def from_dict(cls, data: dict, http, **kwargs):
        """
        Creates an instance of the Embed Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed Embed Instance
        """
        try:
            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise errs.InvalidPassedDataError(f"Failed to perform validation in '{cls.__name__}'",data=data)

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
    def url(self):
        return self._url
    
    @property
    def type(self):
        return self._type
    
    @property 
    def title(self):
        return self._title

    @property 
    def image(self):
        return self._image
    
    @property
    def description(self):
        return self._description        
