import logging
import datetime
import sys
import typing
from marshmallow import Schema, fields, post_load, ValidationError, INCLUDE

from .. import utils
from . import HivenObject
from . import user
from ..exception import InvalidPassedDataError, InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Mention']


class MentionSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    timestamp = fields.Raw(required=True)
    user = fields.Raw(required=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Mention Object
        """
        return Mention(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = MentionSchema()


class Mention(HivenObject):
    """
    Represents an mention for a user in Hiven
    """
    def __init__(self, **kwargs):
        self._timestamp = kwargs.get('timestamp')
        self._user = kwargs.get('user')
        self._author = kwargs.get('author')

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        users: typing.List[user.User]):
        """
        Creates an instance of the Mention Class with the passed data

        :param data: Dict for the data that should be passed
        :param users: The cached users list to fetch the mentioned user and author from
        :return: The newly constructed Mention Instance
        """
        try:
            data['user'] = utils.get(users, id=utils.convert_value(int, data['user']['id']))

            instance = GLOBAL_SCHEMA.load(data, unknown=INCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise InvalidPassedDataError(data=data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!")
            raise InitializationError(f"Failed to initialise {cls.__name__} due to exception:\n"
                                      f"{sys.exc_info()[0].__name__}: {e}!")
        else:
            return instance

    @property
    def timestamp(self):
        return self._timestamp
    
    @property
    def user(self):
        return self._user
    
    @property
    def author(self):
        return self._author
