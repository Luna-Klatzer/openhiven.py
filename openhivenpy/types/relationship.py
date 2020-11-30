import logging
import sys
import asyncio

from ._get_type import getType
from .user import User
from openhivenpy.gateway.http import HTTPClient
from openhivenpy.utils.utils import get
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

class Relationship():
    """`openhivenpy.types.Relationship`
    
    Data Class for a Hiven Relationship
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Represents a relationship with a person 
    
    Possible Types
    ~~~~~~~~~~~~~~
    
    0 - No Relationshiop
    
    1 - Outgoing Friend Request
    
    2 - Incoming Friend Request
    
    3 - Friend
    
    4 - Restricted User
    
    5 - Blocked User
      
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._user_id = data['user_id']
            
            resp = asyncio.run(http_client.request(f"/users/{self._user_id}"))
            user_data = resp.get('data')

            if user_data == None:
                user_data = data['user']            
            self._user = getType.User(user_data, http_client)
            
            self._type = data['type']
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the Relationship object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize Relationship object! Most likely faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the Relationship object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize Relationship object! Possibly faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
    @property
    def user(self) -> User:
        return self._user
    
    @property
    def user_id(self) -> int:
        return self._user_id
    

