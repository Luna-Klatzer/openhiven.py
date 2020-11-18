import logging
import sys
import asyncio

from ._get_type import getType
from .Room import Room
import openhivenpy.Exception as errs
from openhivenpy.Gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class PrivateRoom():
    """`openhivenpy.Types.Room`
    
    Data Class for a Private Chat Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        
        self.recipient = getType.User(data.get("recipients", {}))
        
        self.http_client = http_client
        
        