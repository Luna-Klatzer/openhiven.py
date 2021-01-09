import datetime
import logging
import sys

import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['Typing']


class Typing:
    """`openhivenpy.types.Typing`
    
    Data Class for Typing
    ~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Returned with HivenClient.on_typing_start() and HivenClient.on_typing_end()
    
    """
    def __init__(self, data: dict, member, room, house, http: HTTP):
        try:
            self._author = member
            self._room = room
            self._house = house
            self._author_id = data.get('author_id')
            self._house_id = data.get('house_id')
            self._room_id = data.get('room_id')
            self._timestamp = data.get('timestamp')
            
            self._http = http
                        
        except AttributeError as e: 
            logger.error(f"Failed to initialize the Typing object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Typing object! Most likely faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the Typing object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Typing object! Possibly faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
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
