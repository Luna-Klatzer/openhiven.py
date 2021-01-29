import asyncio
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

    Returned with create_house

    Note! This class is a lazy class and does not have every available data!
    Consider fetching for more data the regular house object with utils.get()

    """

    def __init__(self, data: dict, http):
        self._id = int(data['id']) if data.get('id') is not None else None
        self._name = data.get('name')
        self._icon = data.get('icon')
        self._owner_id = data.get('owner_id')
        self._type = data.get('type')

        _rooms_data = data.get("rooms")
        if _rooms_data:
            self._rooms = list(getType.room(_room_data, http, self) for _room_data in _rooms_data)
        else:
            self._rooms = None

    def __str__(self):
        return self.name

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
    
    Returned with the getHouse() and get_house()
    
    """

    def __init__(
            self,
            data: dict,
            http: HTTP,
            client_id: int):
        """
        Expected JSON-DATA
        -------------------
        rooms: room[{
            type: int,
            recipients: null
            position: int,
            permission_overrides: bits,
            owner_id: string,
            name: string,
            last_message_id: string,
            id: string,
            house_id: string,
            emoji: object,
            description: string,
            default_permission_override: int
          }],
        roles: role[{
            position: int,
            name: string,
            level: int,
            id: string,
            deny: bits,
            color: string,
            allow: bits
          }],
        owner_id: string,
        name: string,
        members: [{
            user_id: string,
            user: {
              username: string,
              user_flags: string,
              name: string,
              id: string,
              icon: string,
              header: string,
              presence: string
            },
            roles: array,
            last_permission_update: string,
            joined_at: string,
            house_id: string
          }],
        id: string,
        icon: string,
        entities: [{
            type: int,
            resource_pointers: [{
              resource_type: string,
              resource_id: string
            }],
            position: int,
            name: string,
            id: string
          }],
        default_permissions: int,
        banner: string
        """
        try:
            for _needed_prop in ['id', 'name', 'banner', 'icon', 'owner_id', 'roles', 'entities',
                                 'default_permissions', 'members', 'rooms']:
                if _needed_prop in data.keys():
                    continue
                else:
                    raise errs.InvalidData(f"Missing '{_needed_prop}' field in passed data", data=data)

            self._id = int(data.get('id'))
            self._name = data.get('name')
            self._banner = data.get('banner')
            self._icon = data.get('icon')
            self._owner_id = data.get('owner_id')

            self._roles = list(data.get('roles'))

            self._categories = []
            for category in data.get('entities'):
                category = getType.category(category, http)
                self._categories.append(category)

            self._default_permissions = data.get('default_permissions')

            _members = data.get("members")
            self._members = list(getType.member(mem_data, self, http) for mem_data in _members)

            self._rooms = list(getType.room(room_data, http, self) for room_data in data.get("rooms"))
            self._client_member = utils.get(self._members, user_id=client_id)

            # TODO! See if possible request is reasonable
            # _raw_data = http.loop.create_task(http.request(endpoint=f"/users/{self._owner_id}"))
            # if _raw_data:
            #     _data = _raw_data.get('data')
            #     if _data:
            #         self._owner = getType.user(
            #             data=_data,
            #             http=http)
            #     else:
            #         raise errs.HTTPReceivedNoData()
            # else:
            #     raise errs.HTTPReceivedNoData()

            self._http = http

        except AttributeError as e:
            logger.error(f"[HOUSE] Failed to initialize the House object! > {sys.exc_info()[0].__name__}, "
                         f"{str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize House object! Most likely faulty data! "
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")

        except Exception as e:
            logger.error(f"[HOUSE] Failed to initialize the House object! > {sys.exc_info()[0].__name__}, "
                         f"{str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize House object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('banner', self.banner),
            ('owner_id', self.owner_id)
        ]
        return '<House {}>'.format(' '.join('%s=%s' % t for t in info))

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
        return f"https://media.hiven.io/v1/houses/{self.id}/icons/{self._icon}"

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

    async def get_member(self, member_id: int):
        """openhivenpy.types.House.get_member()

        Returns a Hiven Member Object based on the passed id.

        Returns the Member if it exists else returns None
        """
        try:
            cached_member = utils.get(self._members, id=member_id)
            if cached_member:
                _raw_data = await self._http.request(f"/houses/{self.id}/users/{member_id}")

                if _raw_data:
                    _data = _raw_data.get('data')
                    if _data:
                        return await getType.a_room(
                            data=_data,
                            http=self._http,
                            house=self)
                    else:
                        raise errs.HTTPReceivedNoData()
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                logger.warning(f"[HOUSE] Found no member with specified id={member_id} in {repr(self)}!")

            return None

        except Exception as e:
            logger.error(f"[HOUSE] Failed to get the member with id {member_id}!"
                         f"> {sys.exc_info()[0].__name__}, {str(e)}")
            return False

    async def get_room(self, room_id: int):
        """openhivenpy.types.House.get_room()

        Returns a Hiven Room Object based on the passed id.

        Returns the Room if it exists else returns None
        """
        try:
            cached_room = utils.get(self._rooms, id=room_id)
            if cached_room:
                return cached_room
                # Not Possible yet
                # data = await self._http.request(f"/rooms/{room_id}")
                # return await getType.a_room(data, self._http)
            else:
                logger.warning(f"[HOUSE] Found no room with specified id={room_id} in the client cache!")

            return None
        except Exception as e:
            logger.error(f"[HOUSE] Failed to get the room with id {room_id} in house {repr(self)} "
                         f"> {sys.exc_info()[0].__name__}, {str(e)}")
            return False

    async def create_room(
            self,
            name: str,
            parent_entity_id: Optional[Union[float, int]] = None) -> Union[getType.room, None]:
        """openhivenpy.types.House.create_room()

        Creates a Room in the house with the specified name. 
        
        Returns a `Room` object of the room that was created if successful
        
        """
        try:
            json = {'name': name}
            if parent_entity_id:
                json['parent_entity_id'] = parent_entity_id
            else:
                category = utils.get(self._categories, name="Rooms")
                json['parent_entity_id'] = category.id

            resp = await self._http.post(
                f"/houses/{self._id}/rooms",
                json=json)

            if resp.status < 300:
                data = (await resp.json()).get('data')
                if data:
                    room = await getType.a_room(data, self._http, self)
                    self._rooms.append(room)
                    return room
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")

        except Exception as e:
            logger.error(f"[HOUSE] Failed to create room '{name}' in house {repr(self)}!"
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")
            return None

    # TODO! Delete Room!

    async def create_category(self, name: str) -> bool:
        """openhivenpy.types.House.create_category()

        Creates a Category in the house with the specified name.

        Returns currently only a bool object since no Category exists yet

        """
        try:
            json = {'name': name, 'type': 1}
            resp = await self._http.post(
                endpoint=f"/houses/{self._id}/entities",
                json=json)

            if resp.status < 300:
                raw_data = await resp.json()
                data = raw_data.get('data')
                if data:
                    category = getType.category(data, self._http)
                    self._categories.append(category)
                    return category
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")

        except Exception as e:
            logger.error(f"[HOUSE] Failed to create category '{name}' in house {repr(self)}!"
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")
            return False

    async def leave(self) -> bool:
        """openhivenpy.types.House.leave()

        Leaves the house.
        
        Returns the house id if successful.
        
        """
        try:
            resp = await self._http.delete(endpoint=f"/users/@me/houses/{self.id}")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")

        except Exception as e:
            logger.error(f"[HOUSE] Failed to leave {repr(self)}! "
                         f"> {sys.exc_info()[0].__name__}, {str(e)}")
            return False

    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.types.House.edit()`
        
        Change the houses data.
        
        Available options: name, icon(base64)
        
        Returns `True` if successful
        
        """
        try:
            for key in kwargs.keys():
                if key in ['name']:
                    resp = await self._http.patch(
                        endpoint=f"/houses/{self.id}",
                        data={key: kwargs.get(key)})

                    if resp.status < 300:
                        return True
                    else:
                        raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
                else:
                    logger.error("[HOUSE] The passed value does not exist in the user context!")
                    raise NameError("The passed value does not exist in the user context!")

        except Exception as e:
            keys = "".join(key + " " for key in kwargs.keys()) if kwargs != {} else None
            logger.error(f"[HOUSE] Failed edit request of values '{keys}' in house {repr(self)}!"
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")
            return False

    async def create_invite(self, max_uses: int) -> Union[str, None]:
        """`openhivenpy.types.House.create_invite()`

        Creates an invite for the current house. 
            
        Returns the invite url if successful.

        """
        try:
            resp = await self._http.post(endpoint=f"/houses/{self.id}/invites")

            if resp.status < 300:
                raw_data = await resp.json()
                data = raw_data.get('data', {})

                if data:
                    code = data.get('code')
                    return f"https://hiven.house/{code}"
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")

        except Exception as e:
            logger.error(f"[HOUSE] Failed to create invite for house {self.name} with id {self.id}!"
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")
            return None

    async def delete(self) -> Union[int, None]:
        """`openhivenpy.types.House.delete()`
        
        Deletes the house if permissions are sufficient!
        
        Returns the house id if successful
        
        """
        try:
            resp = await self._http.delete(f"/houses/{self.id}")

            if resp.status < 300:
                return self.id
            else:
                return None

        except Exception as e:
            logger.error(f"[HOUSE] Failed to delete House {repr(self)}! > {e}")
