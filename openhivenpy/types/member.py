import requests
import logging
import sys

from .user import User
from openhivenpy.types._get_type import getType
from openhivenpy.gateway.http import HTTPClient
from openhivenpy.utils import raise_value_to_type
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

class Member(User):
    """`openhivenpy.types.Member` 
    
    Data Class for a Hiven member
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only) and the User Class!
    
    Returned with house house member list and House.get_member()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient, House):
        try:
            super().__init__(data, http_client)
            self._user_id = int(data['user_id']) if data.get('user_id') != None else None
            self._house_id = data.get('house_id')
            self._joined_at = data.get('joined_at')
            self._roles = raise_value_to_type(data.get('roles', []), list)
            
            self._house = House
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the Member object! Cause of Error: {str(sys.exc_info()[1])}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize Member object! Most likely faulty data! Cause of error: {str(sys.exc_info()[1])}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the Member object! Cause of Error: {str(sys.exc_info()[1])}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize Member object! Possibly faulty data! Cause of error: {str(sys.exc_info()[1])}, {str(e)}")

    def __str__(self):
        return self.id()
        
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
        
        Kick
        ~~~~

        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise `HivenException.Forbidden`. 
            
        Returns `True` if succesful.
        
        """

        #DELETE api.hiven.io/houses/HOUSEID/members/MEMBERID
        res = requests.delete(f"https://api.hiven.io/v1/houses/{self._house_id}/members/{self._user_id}", headers={"Content-Type": "application/json", "Authorization": self._TOKEN})
        if not res.response_code == 204: #Why not continue using 200 instead of using 204 i have no idea.
            raise errs.Forbidden()
        else:
            return True