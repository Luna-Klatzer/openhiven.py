import logging
import sys
from typing import Optional, Union

from ._get_type import getType
from openhivenpy.gateway.http import HTTP
import openhivenpy.utils.utils as utils
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['House', 'LazyHouse']


class LazyHouse:
    """`openhivenpy.types.LazyHouse`

    Low-Level Data Class for a Hiven House
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The class inherits all the available data from Hiven(attr -> read-only)!

    Returned with create_house

    Note! This class is a lazy class and does not have every available data!
    Consider fetching the better house with utils.get()

    """

    def __init__(self, data: dict, http):
        self._id = int(data['id']) if data.get('id') is not None else None
        self._name = data.get('name')
        self._icon = data.get('icon')
        self._owner_id = data.get('owner_id')
        self._rooms = list(getType.room(r, http, self) for r in data.get("rooms"))

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return (f"https://media.hiven.io/v1/houses/"
                f"{self.id}/icons/{self._icon}")

    @property
    def owner_id(self) -> int:
        return self._owner_id

    @property
    def rooms(self) -> list:
        return self._rooms


class House:
    """`openhivenpy.types.House`
    
    Data Class for a Hiven House
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Returned with the getHouse() and get_house()
    
    """
    def __init__(
                self, 
                data: dict,
                http: HTTP,
                client_id: int):
        try:
            self._id = int(data['id']) if data.get('id') is not None else None
            self._name = data.get('name')
            self._banner = data.get('banner')
            self._icon = data.get('icon')
            self._owner_id = data.get('owner_id')
            self._roles = list(data.get('entities', []))
            self._categories = []
            for category in data.get('entities', []):
                category = getType.category(category, http)
                self._categories.append(category)

            self._default_permissions = data.get('default_permissions')

            members = data.get("members", [])
            if members:
                self._members = list(getType.member(m, http, self) for m in members)
            else:
                self._members = []

            self._rooms = list(getType.room(r, http, self) for r in data.get("rooms"))
            self._client_member = utils.get(self._members, user_id=client_id)

            self._http = http
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the House object! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize House object! Most likely faulty data! "
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the House object! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize House object! Possibly faulty data! "
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    @property
    def client_member(self) -> getType.member:
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
        return (f"https://media.hiven.io/v1/houses/"
                f"{self.id}/icons/{self._icon}")
    
    @property
    def owner_id(self) -> int:
        return self._owner_id     
        
    @property
    def roles(self) -> list:
        return self._roles  

    @property
    def categories(self) -> list:
        return self._categories

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
        try:
            cached_member = utils.get(self._members, id=member_id)
            if cached_member:
                data = await self._http.request(f"/houses/{self.id}/users/{member_id}")
                return await getType.a_room(data, self._http, self)
            
            return None
        except Exception as e:
            logger.error(f"Failed to get the room {self.name} with id {self.id}. " 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False
        
    async def get_room(self, room_id: int):
        """openhivenpy.types.House.get_room()

        Returns a Hiven Room Object based on the passed id.

        Returns the Room if it exists else returns None
        """
        try:
            cached_room = utils.get(self._rooms, id=int(room_id))
            if cached_room:
                return cached_room
                # Not Possible yet
                # data = await self._http.request(f"/rooms/{room_id}")
                # return await getType.a_room(data, self._http)
                
            return None
        except Exception as e:
            logger.error(f"Failed to get the room {self.name} with id {self.id}. " 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False

    async def create_room(
                        self,
                        name: str,
                        parent_entity_id: Optional[Union[float, int]] = None) -> Union[getType.room, None]:
        """openhivenpy.types.House.create_room()

        Creates a Room in the house with the specified name. 
        
        Returns a `Room` object of the room that was created if successful
        
        """
        http_code = "Unknown"
        try:
            json = {'name': name}
            if parent_entity_id is not None:
                json['parent_entity_id'] = parent_entity_id
            else:
                category = utils.get(self._categories, name="Rooms")
                json['parent_entity_id'] = category.id
            resp = await self._http.post(
                                                f"/houses/{self._id}/rooms",
                                                json=json)
            http_code = resp.status
            
            if http_code < 300:
                data = (await resp.json()).get('data')
                if data is not None:
                    room = await getType.a_room(await resp.json(), self._http, self)
                    self._rooms.append(room)
                    return room
                else:
                    raise errs.HTTPFaultyResponse()
            else:
                raise errs.HTTPFaultyResponse()

        except Exception as e:
            logger.error(f"Failed to create the room {self.name} with id {self.id}." 
                         f"[CODE={http_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None

    async def create_category(self, name: str) -> bool:
        """openhivenpy.types.House.create_category()

        Creates a Category in the house with the specified name.

        Returns currently only a bool object since no Category exists yet

        """
        http_code = "Unknown"
        try:
            json = {'name': name, 'type': 1}
            resp = await self._http.post(f"/houses/{self._id}/entities",
                                                json=json)
            http_code = resp.status

            if http_code < 300:
                data = await resp.json()
                category = getType.category(data.get('data'), self._http)
                self._categories.append(category)
                return category
            else:
                raise errs.HTTPFaultyResponse()

        except Exception as e:
            logger.error(f"Failed to create the room {self.name} with id {self.id}."
                         f"[CODE={http_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False

    async def leave(self) -> bool:
        """openhivenpy.types.House.leave()

        Leaves the house.
        
        Returns the house id if successful.
        
        """
        http_code = "Unknown"
        try:
            resp = await self._http.delete(f"/users/@me/houses/{self.id}")
            http_code = resp.status

            if resp.status < 300:
                return True
            else:
                return False
        
        except Exception as e:
            logger.error(f"Failed to leave the house {self.name} with id {self.id}." 
                         f"[CODE={http_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False

    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.types.House.edit()`
        
        Change the houses data.
        
        Available options: name, icon(base64)
        
        Returns `True` if successful
        
        """
        http_code = "Unknown"
        keys = "".join(key+" " for key in kwargs.keys()) if kwargs != {} else None
        try:
            for key in kwargs.keys():
                if key in ['name']:
                    resp = await self._http.patch(endpoint=f"/houses/{self.id}",
                                                             data={key: kwargs.get(key)})
                    http_code = resp.status
                    if resp is None:
                        raise errs.HTTPFaultyResponse()
                    else:
                        return True
                else:
                    logger.error("The passed value does not exist in the user context!")
                    raise KeyError("The passed value does not exist in the user context!")
    
        except Exception as e:
            logger.error(f"Failed to change the values {keys} for house {self.name} with id {self.id}." 
                         f"[CODE={http_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False

    async def create_invite(self, max_uses: int) -> Union[str, None]:
        """`openhivenpy.types.House.create_invite()`

        Creates an invite for the current house. 
            
        Returns the invite url if successful.

        """
        http_code = "Unknown"
        try:
            resp = await self._http.post(endpoint=f"/houses/{self.id}/invites")
            http_code = resp.status
            
            if http_code < 300:
                data = (await resp.json()).get('data', {})
                code = data.get('code')
                if data is not None:
                    return f"https://hiven.house/{code}"
                else:
                    raise errs.HTTPFaultyResponse()
            else:
                raise errs.HTTPFaultyResponse()
    
        except Exception as e:
            logger.error(f"Failed to create invite for house {self.name} with id {self.id}." 
                         f"[CODE={http_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None

    async def delete(self) -> Union[int, None]:
        """`openhivenpy.types.House.delete()`
        
        Deletes the house if permissions are sufficient!
        
        Returns the house id if successful
        
        """
        http_code = "Unknown"
        try:
            resp = await self._http.delete(f"/houses/{self.id}")
            http_code = resp.status

            if resp.status < 300:
                return self.id
            else:
                return None
         
        except Exception as e:
            logger.error(f"Failed to delete House! [CODE={http_code}] Cause of error: {e}")
