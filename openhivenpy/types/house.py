import logging
import sys
import requests

from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient
from openhivenpy.utils.utils import get
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

class House():
    r"""`openhivenpy.types.House`
    
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
            logger.error(f"Failed to initialize the House object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize House object! Most likely faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the House object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize House object! Possibly faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

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
        """openhivenpy.types.House.get_member()

        Returns a Hiven Member Object based on the passed id.

        Returns the Member if it exists else returns None
        """
        if get(self._members, id=member_id):
            data = await self._http_client.request(f"/houses/{self.id}/users/{member_id}")
            return await getType.a_Room(data, self._http_client)
        return None

    async def get_room(self, room_id: int):
        """openhivenpy.types.House.get_room()

        Returns a Hiven Room Object based on the passed id.

        Returns the Room if it exists else returns None
        """
        cached_room = get(self._rooms, id=int(room_id))
        if cached_room:
            return cached_room
            # Not Possible yet
            # data = await self._http_client.request(f"/rooms/{room_id}")
            # return await getType.a_Room(data, self._http_client)
        return None

    async def create_room(self, name) -> getType.Room:
        """openhivenpy.types.House.create_room(name)

        Creates a Room in the house with the specified name. 
        
        Returns the Room that was created if successful
        
        """
        res = await self._http_client.post(f"https://api.hiven.io/v1/houses/{self._id}/rooms")
        return await getType.a_Room(await res.json(), self._http_client)

    async def leave(self, house_id: int) -> bool:
        """openhivenpy.types.House.leave()

        Leaves the house.
        
        Returns `True` if successful.
        
        """
        res = await self._http_client.delete(f"https://api.hiven.io/v1/houses/{self._id}")
        return res.status_code == 204 or res.status_code == 200

    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.types.House.edit()`
        
        Change the houses data.
        
        Available options: name, base64 (icon)
        
        Returns `True` if successful
        
        """
        execution_code = None
        keys = "".join(key+" " for key in kwargs.keys()) if kwargs != {} else None
        try:
            for key in kwargs.keys():
                if key in ['name']:
                    response = await self._http_client.patch(endpoint=f"/houses/{self.id}", data={key: kwargs.get(key)})
                    if response == None:
                        logger.debug(f"Failed to change the values {keys}for house {self.name} with id {self.id}!")
                        return False
                    else:
                        execution_code = response.status
                        return True
                else:
                    logger.error("The passed value does not exist in the user context!")
                    raise KeyError("The passed value does not exist in the user context!")
    
        except Exception as e:
            logger.critical(f"Failed to change the values {keys} for house {self.name} with id {self.id}. [CODE={execution_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HTTPRequestError(f"Failed to edit {keys}! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")   


    async def create_invite(self) -> str:
        """
            `openhivenpy.types.House.create_invite()`

            Creates an invite for the current house. Returns the invite if successful.

        """
        res = await self._http_client.post(endpoint=f"/houses/{self.id}/invites")
        x = await res.json()
        return f"https://hiven.house/{x['data']['code']}"
