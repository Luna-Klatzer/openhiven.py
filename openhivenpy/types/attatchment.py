import logging

from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['Attachment']


class Attachment:
    """`openhivenpy.types.Attachment` 
    
    Data Class for a Attachment
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents a Hiven Attachment
    
    """
    def __init__(self, data: dict, http: HTTP):
        self._filename = data["filename"]
        self._media_url = data["media_url"]
        self._raw = data
        self._http = http

    def __str__(self):
        return self.filename

    @property
    def filename(self):
        return self._filename

    @property
    def media_url(self):
        return self._media_url
    
    @property
    def raw(self):
        # Different files have different attribs
        return self._raw
