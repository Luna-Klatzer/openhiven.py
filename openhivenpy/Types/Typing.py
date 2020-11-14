import datetime
import logging
import sys

import openhivenpy.Exception as errs
from openhivenpy.Types import *
import openhivenpy.Utils as utils 

logger = logging.getLogger(__name__)

class Typing():
    """`openhivenpy.Types.Typing`
    
    Data Class for Typing
    ~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with HivenClient.on_typing_start() and HivenClient.on_typing_end()
    
    """
    def __init__(self, data: dict, auth_token: str):
        try:
            self.AUTH_TOKEN = auth_token
            self._member = data.get('author_id')
            self._house = data.get('house_id')
            self._room = data.get('room_id')
            self._timestamp = data.get('timestamp')
            
        except AttributeError as e: 
            logger.error(e)
            raise errs.FaultyInitialization("The data of the object Room was not initialized correctly")
        
        except Exception as e: 
            logger.error(e)
            raise sys.exc_info()[0](e)

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._timestamp)