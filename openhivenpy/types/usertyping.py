import datetime
import logging
import sys
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['UserTyping']


class UserTyping(HivenObject):
    """
    Represents a Hiven User Typing in a room
    """
    def __init__(self, data: dict, member, room, house, http):
        try:
            self._author = member
            self._room = room
            self._house = house
            self._author_id = data.get('author_id')
            self._house_id = data.get('house_id')
            self._room_id = data.get('room_id')
            self._timestamp = data.get('timestamp')
            
            self._http = http
        
        except Exception as e:
            utils.log_traceback(msg="[TYPING] Traceback:",
                                suffix="Failed to initialize the Typing object! \n"
                                       f"{sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Typing object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('house_id', self.house_id),
            ('author_id', self.author_id),
            ('room_id', self.room_id),
            ('author', repr(self.author))
        ]
        return '<Typing {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._timestamp)

    @property
    def author(self):
        return self._author

    @property
    def house(self):
        return self._house

    @property
    def room(self):
        return self._room

    @property
    def author_id(self):
        return self._author_id

    @property
    def house_id(self):
        return self._house_id

    @property
    def room_id(self):
        return self._room_id
