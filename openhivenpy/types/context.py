import logging
import sys
from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from .. import utils
from . import HivenObject
from .. import exception as errs

logger = logging.getLogger(__name__)

__all__ = ('Context', 'ContextSchema')


class ContextSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    room = fields.Raw(required=True)
    author = fields.Raw(required=True)
    created_at = fields.Str(required=True)
    house = fields.Raw(default=None)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Context Object
        """
        return Context(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = ContextSchema()


class Context(HivenObject):
    """
    Represents a Command Context for a triggered command in the CommandListener
    """
    def __init__(self, **kwargs):
        """
        Object Instance Construction

        :param kwargs: Additional Parameter of the class that will be initialised with it
        """
        self._room = kwargs.get('room')
        self._author = kwargs.get('author')
        self._house = kwargs.get('house')
        self._created_at = kwargs.get('created_at')

    @classmethod
    async def from_dict(cls, data: dict, http, **kwargs):
        """
        Creates an instance of the Context Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed Context Instance
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
    def house(self):
        return self._house

    @property
    def author(self):
        return self._author

    @property
    def room(self):
        return self._room

    @property
    def created_at(self):
        return self._created_at
