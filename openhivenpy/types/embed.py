import logging

from ._get_type import getType
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Embed():
    """`openhivenpy.types.Embed`
    
    Data Class for a Embed Object
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with a message object if an embed object is added
    
    Attributes
    ~~~~~~~~~~
    
    url: `str` - Endpoint of the embed object
    
    type: `str` - Type of the embed message
    
    title: `str` - Title that displays on the embed object
    
    image: `str` - Url for the image (Currently not in correct format)
    
    description: `str` - Description of the embed object
    
    """
    def __init__(self, data: dict):
        self._url = int(data.get('url'))
        self._type = int(data.get('type'))
        self._title = int(data.get('title'))
        self._image = int(data.get('image'))
        self._description = int(data.get('description'))
        
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

        
        