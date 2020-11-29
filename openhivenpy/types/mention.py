import asyncio
import logging

from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Mention:
    """`openhivenpy.types.Mention`
    
    Data Class for a Mention
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    Represents an mention for a user in Hiven
    
    Attributes
    ~~~~~~~~~~
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        self._http_client = http_client