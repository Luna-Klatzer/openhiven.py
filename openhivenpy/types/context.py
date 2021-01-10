import logging

import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP
from ._get_type import getType

logger = logging.getLogger(__name__)

__all__ = ['Context']


class Context:
    """`openhivenpy.types.Context` 
    
    Data Class for a Command Context
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Returned with events, commands and HivenClient.on_ready()
    
    """
    def __init__(self, data: dict, http: HTTP):
        self._http = http
        self._room = None
        self._author = None
        self._house = None
        self._created_at = None

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('author', repr(self.author)),
            ('room', self.room),
            ('house', self.house),
            ('created_at', self.created_at)
        ]
        return '<Context {}>'.format(' '.join('%s=%s' % t for t in info))

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
