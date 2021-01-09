import logging
from datetime import datetime
from typing import Union

from ._get_type import getType
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['Mention']


class Mention:
    """`openhivenpy.types.Mention`
    
    Data Class for a Mention
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    Represents an mention for a user in Hiven
    
    Simple User Object
    
    Attributes
    ~~~~~~~~~~
    
    timestamp: `datetime.timestamp` - Creation date of the mention
    
    author: `openhivenpy.types.User` - Author that created the mention
    
    """
    def __init__(self, data: dict, timestamp: Union[datetime, str], author, http: HTTP):
        # Converting to seconds because it's in milliseconds
        if data.get('timestamp') is not None:
            self._timestamp = datetime.fromtimestamp(int(timestamp) / 1000) 
        else:
            self._timestamp = None
            
        self._user = getType.user(data, http)
            
        self._author = author
        self._http = http

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('timestamp', self.timestamp),
            ('user', repr(self.user)),
            ('author', self.author)
        ]
        return '<Mention {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def timestamp(self):
        return self._timestamp
    
    @property
    def user(self):
        return self._user
    
    @property
    def author(self):
        return self._author
