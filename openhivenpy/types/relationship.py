import logging
import sys

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
    
    Represents a relationship with a person (friend)
      
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._user = data['user']
            self._user['icon'] = f"https://media.hiven.io/v1/users/{self._user['id']}/icons/{self._user['icon']}"
            self._user['header'] = f"https://media.hiven.io/v1/users/{self._user['id']}/headers/{self._user['header']}"
            self._user_id = data['user_id']
            
            self.http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Unable to initialize the Relationship object! Cause of Error: {e}")
            raise errs.FaultyInitialization("The data of the object Relationship is not in correct Format")
        
        except Exception as e: 
            logger.error(f"Unable to initialize the Relationship object! Cause of Error: {e}")
            raise sys.exc_info()[-1](e)
        
    @property
    def user(self) -> User:
        return self._user
    
    @property
    def user_id(self) -> int:
        return self._user_id

