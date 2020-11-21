import logging
import sys
import requests

from ._get_type import getType
from openhivenpy.Gateway.http import HTTPClient
from openhivenpy.Utils.utils import get
import openhivenpy.Exception as errs

logger = logging.getLogger(__name__)

class House():
    r"""`openhivenpy.Types.House`
    
    Data Class for a Hiven House
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with the getGuild() and get_guild()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient, client_id: int):
        try:
            self._id = int(data['id']) if data.get('id') != None else None
            self._name = data.get('name')
            self._banner = data.get('banner')
            self._icon = data.get('icon')
            self._owner_id = data.get('owner_id')
            self._roles = list(data.get('entities'))
            self._members = list(getType.Member(m, http_client, self) for m in data.get("members"))
            self._rooms = list(getType.Room(r, http_client, self) for r in data.get("rooms"))
        
            self._client_member = get(self._members, user_id=client_id)
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Error while initializing a House object: {e}")
            raise errs.FaultyInitialization("The data of the object House is not in correct Format")
        
        except Exception as e: 
            logger.error(f"Error while initializing a House object: {e}")
            raise sys.exc_info()[0](e)

    @property
    def client_member(self) -> getType.Member:
        return self._client_member

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

    async def get_member(self, member_id):
        if get(self._members, id=member_id):
            data = await self.connection.http_client.request(endpoint=f"/houses/{self.id}/users/{member_id}")
            return await getType.a_Room(data, self.connection.http_client)
        return None

    async def create_room(self, name) -> getType.Room:
        """openhivenpy.Types.House.create_room(name)

        Creates a Room in the house with the specified name. 
        
        Returns the Room that was created if successful
        
        """
        res = requests.post(f"https://api.hiven.io/v1/houses/{self._id}/rooms", headers={"Content-Type": "application/json", "Authorization": self._TOKEN})
        return res #ToDo

    async def leave(self, house_id: int) -> bool:
        """openhivenpy.Types.House.leave()

        Leaves the house.
        
        Returns `True` if successful.
        
        """
        res = requests.delete(f"https://api.hiven.io/v1/houses/{self._id}", headers={"Content-Type": "application/json", "Authorization": self._TOKEN})
        return res.status_code == 200