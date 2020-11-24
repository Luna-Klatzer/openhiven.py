import logging
import sys

from ._get_type import getType
from .user import User
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class PrivateRoom():
    """`openhivenpy.types.PrivateRoom`
    
    Data Class for a Private Chat Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Represents a private chat room with a person
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._id = int(data['id']) if data.get('id') != None else None
            self._last_message_id = data.get('last_message_id')
            recipients = data.get("recipients")
            self._recipient = getType.User(recipients[0], http_client)
            self._name = f"Private chat with {recipients[0]['name']}"   
            self._type = data.get('type')
             
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the PrivateRoom object! Cause of Error: {str(sys.exc_info()[1])}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize PrivateRoom object! Most likely faulty data! Cause of error: {str(sys.exc_info()[1])}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the PrivateRoom object! Cause of Error: {str(sys.exc_info()[1])}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize PrivateRoom object! Possibly faulty data! Cause of error: {str(sys.exc_info()[1])}, {str(e)}")
        
    @property
    def user(self) -> User:
        return self._recipient
    
    @property
    def recipient(self) -> User:
        return self._recipient
    
    @property
    def id(self) -> User:
        return self._id

    @property
    def last_message_id(self) -> User:
        return self._last_message_id    
        
    @property
    def name(self) -> User:
        return self._name 

    @property
    def type(self) -> User:
        return self._type 
