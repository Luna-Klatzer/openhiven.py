import logging
import sys
import asyncio

from ._get_type import getType
from .user import User
from openhivenpy.gateway.http import HTTP
from openhivenpy.utils.utils import get
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['Relationship']


class Relationship:
    """`openhivenpy.types.Relationship`
    
    Data Class for a Hiven Relationship
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents a relationship with a person 
    
    Possible Types
    ~~~~~~~~~~~~~~
    
    0 - No Relationship
    
    1 - Outgoing Friend Request
    
    2 - Incoming Friend Request
    
    3 - Friend
    
    4 - Restricted User
    
    5 - Blocked User
      
    """
    def __init__(self, data: dict, http: HTTP):
        try:
            self._user_id = data.get('user_id')
            resp = asyncio.run(http.request(f"/users/{self._user_id}"))
            user_data = resp.get('data')
            if user_data is None:
                user_data = data.get('user')

            self._user = getType.user(user_data, http)
            self._type = data.get('type')
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"[RELATIONSHIP] Failed to initialize the Relationship object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Relationship object! Most likely faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"[RELATIONSHIP] Failed to initialize the Relationship object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Relationship object! Possibly faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('user_id', self.user_id),
            ('user', repr(self.user)),
            ('type', self.type)
        ]
        return '<Relationship {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user(self) -> User:
        return self._user
    
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def type(self):
        return self._type
