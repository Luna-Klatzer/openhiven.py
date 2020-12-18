import logging
import sys

from .user import User
from openhivenpy.types._get_type import getType
from openhivenpy.gateway.http import HTTP
from openhivenpy.utils import raise_value_to_type
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['Member']


class Member(User):
    """`openhivenpy.types.Member` 
    
    Data Class for a Hiven member
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only) and the User Class!
    
    Returned with house house member list and House.get_member()
    
    """
    def __init__(self, data: dict, http: HTTP, house):
        try:
            super().__init__(data, http)
            self._user_id = int(data['user_id']) if data.get('user_id') is not None else None
            self._house_id = data.get('house_id')
            self._joined_at = data.get('joined_at')
            self._roles = raise_value_to_type(data.get('roles', []), list)
            
            self._house = house
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the Member object! " 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Most likely faulty data! " 
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the Member object! " 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Possibly faulty data! " 
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self):
        return self.id
        
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def joined_house_at(self) -> str:
        return self._joined_at

    @property
    def house_id(self) -> int:
        return self._house_id

    @property
    def roles(self) -> list:
        return self._roles

    async def kick(self) -> bool:
        """`openhivenpy.types.Member.kick()`

        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise `HivenException.Forbidden`. 
            
        Returns `True` if successful.
        
        """
        resp = await self._http.delete(f"/{self._house_id}/members/{self._user_id}")
        if not resp.status < 300:
            raise errs.Forbidden()
        else:
            return True
