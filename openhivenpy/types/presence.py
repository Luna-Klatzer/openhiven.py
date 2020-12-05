import asyncio
import logging

from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

__all__ = ['Presence']


class Presence:
    """`openhivenpy.types.Presence`
    
    Data Class for a User Presence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents a User Presence
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        self._http_client = http_client
