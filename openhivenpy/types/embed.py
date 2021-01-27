import logging

from ._get_type import getType
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['Embed']


class Embed:
    """`openhivenpy.types.Embed`
    
    Data Class for a Embed Object
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Returned with a message object if an embed object is added
    
    Attributes
    ~~~~~~~~~~
    
    url: `str` - Endpoint of the embed object
    
    type: `str` - Type of the embed message
    
    title: `str` - Title that displays on the embed object
    
    image: `dict or str` - Url for the image (Currently not in correct format)
                           or dict with data for a video file
    
    description: `str` - Description of the embed object
    
    """
    def __init__(self, data: dict):
        self._url = data.get('url')
        self._type = data.get('type')
        self._title = data.get('title')
        self._image = data.get('image')
        self._description = data.get('description')

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('url', self.url),
            ('type', self.type),
            ('title', self.title),
            ('image', self.image),
            ('description', self.description)
        ]
        return '<Embed {}>'.format(' '.join('%s=%s' % t for t in info))

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
