import logging
import sys
import requests

from ._get_type import getType
from openhivenpy.Gateway.http import HTTPClient
import openhivenpy.Exception as errs

logger = logging.getLogger(__name__)

class House():
    """`openhivenpy.Types.House`
    
    Data Class for a Hiven House
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with events, the client guilds attribute and get_guild()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._id = data.get('id')
            self._name = data.get('name')
            self._banner = data.get('banner')
            self._icon = data.get('icon')
            self._owner_id = data.get('owner_id')
            self._roles = list(data.get('entities'))
            self._members = list(getType.Member(x, http_client) for x in data.get("members"))
            self._rooms = list(getType.Room(x, http_client) for x in data.get("rooms"))
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Error while initializing a House object: {e}")
            raise errs.FaultyInitialization("The data of the object House was not initialized correctly")
        
        except Exception as e: 
            logger.error(f"Error while initializing a House object: {e}")
            raise sys.exc_info()[0](e)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def banner(self) -> str:
        return self._banner

    @property
    def icon(self) -> str:
        return self._icon
    
    @property
    def owner_id(self) -> int:
        return self._owner_id     
        
    @property
    def roles(self) -> list:
        return self._roles  

    @property
    def users(self) -> list:
        return self._members    
    
    @property
    def members(self) -> list:
        return self._members    
    
    @property
    def rooms(self) -> list:
        return self._rooms    

    @staticmethod
    def create_room(self, name) -> getType.Room:
        """openhivenpy.Types.House.create_room(name)

        Creates a Room in the house with the specified name. 
        
        Returns the Room that was created if successful
        
        """
        res = requests.post(f"https://api.hiven.io/v1/houses/{self._id}/rooms", headers={"Content-Type": "application/json", "Authorization": self._TOKEN})
        return res #ToDo

    @staticmethod
    def leave(self, house_id: int) -> bool:
        """openhivenpy.Types.House.leave()

        Leaves the house.
        
        Returns `True` if successful.
        
        """
        res = requests.delete(f"https://api.hiven.io/v1/houses/{self._id}", headers={"Content-Type": "application/json", "Authorization": self._TOKEN})
        return res.status_code == 200