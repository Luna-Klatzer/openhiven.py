import asyncio
import logging
import datetime

from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Mention():
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
    def __init__(self, data: dict, timestamp: str, author, http_client: HTTPClient):
        # Converting to seconds because it's in miliseconds
        if data.get('timestamp') != None:
            self._timestamp = datetime.fromtimestamp(int(timestamp) / 1000) 
        else:
            self._timestamp = None
            
        self._user = getType.User(data, http_client)
            
        self._author = author
        self._http_client = http_client
        
    @property
    def timestamp(self):
        return self._timestamp
    
    @property
    def user(self):
        return self._user
    
    @property
    def author(self):
        return self._author
        
        