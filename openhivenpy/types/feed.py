import asyncio
import logging

from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Feed:
    """`openhivenpy.types.Feed`
    
    Data Class for a users's Feed
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Represents the feed that is displayed on Hiven
    
    Attributes
    ~~~~~~~~~~
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        self._http_client = http_client