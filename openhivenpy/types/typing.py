import datetime
import logging
import sys

import openhivenpy.exceptions as errs
from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Typing():
    """`openhivenpy.types.Typing`
    
    Data Class for Typing
    ~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with HivenClient.on_typing_start() and HivenClient.on_typing_end()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._member = data.get('author_id')
            self._house = data.get('house_id')
            self._room = data.get('room_id')
            self._timestamp = data.get('timestamp')
            
            self._http_client = http_client
                        
        except AttributeError as e: 
            logger.error(f"Unable to initialize the Typing object! Cause of Error: {str(e)}")
            raise errs.FaultyInitialization("The data of the object Room is not in correct Format")
        
        except Exception as e: 
            logger.error(f"Unable to initialize the Typing object! Cause of Error: {str(e)}")
            raise sys.exc_info()[1](e)

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._timestamp)