import logging
import datetime
import typing
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from . import user

logger = logging.getLogger(__name__)

__all__ = ['Mention']


class Mention(HivenObject):
    """
    Represents an mention for a user in Hiven
    """
    def __init__(self, data: dict, timestamp: typing.Union[datetime.datetime, str], author, http):
        # Converting to seconds because it's in milliseconds
        if data.get('timestamp') is not None:
            self._timestamp = datetime.datetime.fromtimestamp(int(timestamp) / 1000)
        else:
            self._timestamp = None
            
        self._user = user.User(data, http)
            
        self._author = author
        self._http = http

    @property
    def timestamp(self):
        return self._timestamp
    
    @property
    def user(self):
        return self._user
    
    @property
    def author(self):
        return self._author
