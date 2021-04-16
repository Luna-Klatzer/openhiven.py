# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import typing
import fastjsonschema

from . import HivenTypeObject, check_valid
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Member, Room, Entity, Invite
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['House', 'LazyHouse']


class LazyHouse(HivenTypeObject):
    """
    Represents a Hiven House which can contain rooms and entities

    Note! This class is a lazy class and does not have every available data!

    Consider fetching for more data the regular house object with HivenClient.get_house()
    """
    json_schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'name': {'type': 'string'},
            'icon': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
            },
            'owner_id': {'type': 'string'},
            'owner': {'default': None},
            'rooms': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'}
                ],
                'default': {}
            },
            'type': {
                'anyOf': [
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
            },
            'client_member': {
                'anyOf': [
                    {'type': 'integer'},
                    {'type': 'string'},
                    {'type': 'object'},
                    {'type': 'null'}
                ],
            },
        },
        'required': ['id', 'name', 'owner_id']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        """
        Represents a Hiven House which can contain rooms and entities

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        try:
            self._id = data.get('id')
            self._name = data.get('name')
            self._icon = data.get('icon')
            self._owner_id = data.get('owner_id')
            self._owner = data.get('owner')
            self._rooms = data.get('rooms')
            self._type = data.get('type')

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{self.__class__.__name__}' Validation:",
                suffix=f"Failed to initialise {self.__class__.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {self.__class__.__name__} due to an exception occurring"
            ) from e
        else:
            self._client = client

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('owner_id', self.owner_id)
        ]
        return '<House {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> typing.Optional[dict]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['houses'][self.id]

    @classmethod
    @check_valid
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!
        Only exceptions are member objects which are unique in every house

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        data = cls.validate(data)
        if not data.get('owner_id') and data.get('owner'):
            owner = data.pop('owner')
            if type(owner) is dict:
                owner_id = owner.get('id')
            elif isinstance(owner, HivenTypeObject):
                owner_id = getattr(owner, 'id', None)
            else:
                owner_id = None

            if owner_id is None:
                raise InvalidPassedDataError("The passed owner is not in the correct format!", data=data)
            else:
                data['owner_id'] = owner_id

        if type(data.get('members')) is list:
            members = data['members']
            data['members'] = {}
            for member_ in members:
                id_ = member_['user_id'] if member_.get('user_id') else member_.get('user').get('id')
                data['members'][id_] = utils.update_and_return(member_, {'user': id_})

        if type(data.get('roles')) is list:
            roles = data['roles']
            data['roles'] = {}
            for role in roles:
                id_ = role.get('id')
                data['roles'][id_] = role

        if type(data.get('rooms')) is list:
            data['rooms'] = [i['id'] for i in data['rooms']]

        if type(data.get('entities')) is list:
            data['entities'] = [i['id'] for i in data['entities']]

        data['owner'] = data['owner_id']
        return data

    @property
    def id(self) -> typing.Optional[str]:
        return getattr(self, '_id', None)

    @property
    def name(self) -> typing.Optional[str]:
        return getattr(self, '_name', None)

    @property
    def type(self) -> typing.Optional[int]:
        return getattr(self, '_type', None)

    @property
    def icon(self) -> typing.Optional[str]:
        if getattr(self, '_icon', None):
            return "https://media.hiven.io/v1/houses/{}/icons/{}".format(self.id, self._icon)
        else:
            return None

    @property
    def owner_id(self) -> typing.Optional[int]:
        return getattr(self, '_owner_id', None)

    @property
    def rooms(self) -> typing.Optional[list]:
        from . import Room
        if type(self._rooms) is list:
            if type(self._rooms[0]) is str:
                rooms = []
                for d in self._rooms:
                    room_data = self._client.storage['rooms']['house'][d]
                    rooms.append(Room(room_data, client=self._client))

                self._rooms = rooms
            return self._rooms
        else:
            return None


class House(LazyHouse):
    """ Represents a Hiven House which can contain rooms and entities """
    json_schema = {
        'type': 'object',
        'properties': {
            **LazyHouse.json_schema['properties'],
            'entities': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'}
                ],
                'default': {}
            },
            'members': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'}
                ],
                'default': {}
            },
            'roles': {
                'anyOf': [
                    {'type': 'object'},
                    {'type': 'array'},
                    {'type': 'null'}
                ],
                'default': {},
            },
            'banner': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None,
            },
            'default_permissions': {
                'anyOf': [
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None,
            }
        },
        'additionalProperties': False,
        'required': [*LazyHouse.json_schema['required'], 'entities', 'members', 'roles']
    }
    json_validator = fastjsonschema.compile(json_schema)

    def __init__(self, data: dict, client: HivenClient):
        try:
            self._roles = data.get('roles')
            self._roles_data = self._roles
            self._entities: list = data.get('entities')
            self._default_permissions = data.get('default_permissions')
            self._members: dict = data.get('members')
            self._member_data = self._members
            self._client_member = data.get('client_member')
            self._banner = data.get('banner')
            self._owner = data.get('owner')
            self._client = client

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{self.__class__.__name__}' Validation:",
                suffix=f"Failed to initialise {self.__class__.__name__} due to exception:\n"
                       f"{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {self.__class__.__name__} due to an exception occurring"
            ) from e
        super().__init__(data, client)

    @classmethod
    @check_valid
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a new class instance
        """
        data = cls.validate(data)
        data = LazyHouse.format_obj_data(data)
        if data.get('owner_id') is not None:
            data['owner'] = data.get('owner_id')
        elif data['owner'].get('id') is not None:
            data['owner'] = data['owner']['id']
        else:
            raise InvalidPassedDataError(
                "The passed data does not contain a valid owner_id property or owner property containing the id value",
                data=data
            )
        return data

    @property
    def owner(self) -> typing.Optional[Member]:
        from . import Member
        if type(self._owner) is str:
            data = self.get_cached_data()['members'].get(self._owner)
            if data:
                data['user'] = self._client.storage['users'][data['user_id']]
                self._owner = Member(data=data, client=self._client)
                return self._owner
            else:
                return None

        elif type(self._owner) is Member:
            return self._owner
        else:
            return None

    @property
    def client_member(self) -> typing.Optional[Member]:
        return getattr(self, '_client_member', None)

    @property
    def banner(self) -> typing.Optional[str]:
        return getattr(self, '_banner', None)

    @property
    def roles(self) -> typing.Optional[list]:
        return getattr(self, '_roles', None)

    @property
    def entities(self) -> typing.Optional[typing.List[Entity]]:
        from . import Entity
        if type(self._entities) is list:
            if type(self._entities[0]) is str:
                entities = []
                for d in self._entities:
                    entity_data = self._client.storage['entities'][d]
                    entities.append(Entity(entity_data, client=self._client))

                self._entities = entities
            return self._entities
        else:
            return None

    @property
    def users(self) -> typing.Optional[typing.List[Member]]:
        return getattr(self, 'members')

    @property
    def members(self) -> typing.Optional[typing.List[Member]]:
        from . import Member
        if type(self._members) is dict:
            entities = []
            for d in dict(self._members).values():
                member_data = Member.format_obj_data(dict(d))
                member_data['user'] = self._client.storage['users'][dict(d)['user_id']]
                entities.append(Member(member_data, client=self._client))

            self._members = entities
            return self._members
        if type(self._members) is list:
            return self._members
        else:
            return None

    @property
    def default_permissions(self) -> typing.Optional[int]:
        return getattr(self, '_default_permissions', None)

    def get_member(self, member_id: str) -> typing.Optional[Member]:
        """
        Fetches a member from the cache based on the id

        :return: The Member Instance if it exists else returns None
        """
        try:
            from . import Member

            cached_member = self.find_member(member_id)
            if cached_member:
                return Member(cached_member, self._client)

            return None

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to get the member with id {member_id}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            raise

    def find_member(self, member_id: str) -> typing.Optional[dict]:
        """
        Fetches the raw data of a member

        :param member_id: The id of the member which should be fetched
        :return: The data in the cache if it was found
        """
        return self._member_data.get(member_id)

    def get_room(self, room_id: str) -> typing.Optional[Room]:
        """
        Fetches a room from the cache based on the id

        :return: The Room Instance if it exists else returns None
        """
        try:
            from . import Room
            cached_room = self.find_room(room_id)
            if cached_room:
                return Room(cached_room, self._client)

            return None

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to get the room with id {room_id} in house {repr(self)}: \n"
                       f"{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return None

    def find_room(self, room_id: str) -> typing.Optional[dict]:
        """
        Fetches the raw data of a room

        :param room_id: The id of the room which should be fetched
        :return: The data in the cache if it was found
        """
        return self._client.storage['rooms']['house'].get(room_id)

    def get_entity(self, entity_id: str) -> typing.Optional[Entity]:
        """
        Fetches a entity from the cache based on the id

        :return: The Entity Instance if it exists else returns None
        """
        try:
            from . import Entity
            cached_entity = self.find_entity(entity_id)
            if cached_entity:
                return Entity(cached_entity, self._client)

            return None

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to get the member with id {entity_id}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return None

    def find_entity(self, entity_id: str) -> typing.Optional[dict]:
        """
        Fetches the raw data of a entity

        :param entity_id: The id of the entity which should be fetched
        :return: The data in the cache if it was found
        """
        return self._client.storage['entities'].get(entity_id)

    async def create_room(self, name: str, parent_entity_id: typing.Optional[int] = None) -> typing.Optional[Room]:
        """
        Creates a Room in the house with the specified name. 
        
        :return: A Room Instance for the Hiven Room that was created if successful else None
        """
        try:
            from . import Room
            default_entity = utils.get(self.entities, name="Rooms")
            json = {
                'name': name,
                'parent_entity_id': parent_entity_id if parent_entity_id else default_entity.id
            }

            # Creating the room using the api
            resp = await self._client.http.post(f"/houses/{self._id}/rooms", json=json)
            raw_data = await resp.json()

            data = Room.format_obj_data(raw_data.get('data'))
            return Room(data, self._client)

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to create room '{name}' in house {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return None

    async def create_entity(self, name: str) -> typing.Optional[Entity]:
        """
        Creates a entity in the house with the specified name.

        :param name: The name of the new entity
        :return: The newly created Entity Instance
        """
        try:
            resp = await self._client.http.post(
                endpoint=f"/houses/{self.id}/entities",
                json={'name': name, 'type': 1}
            )
            raw_data = await resp.json()

            data = raw_data.get('data')

            # Fetching all existing ids
            existing_entity_ids = [e['id'] for e in self.entities]
            for d in data:
                id_ = d.get('id')
                if id_ not in existing_entity_ids:
                    d = Entity.format_obj_data(d)
                    _entity = Entity(d, self._client)
                    self._entities.append(_entity)
                    return _entity

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to create category '{name}' in house {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return None

    async def leave(self) -> bool:
        """
        Leaves the house
        
        :return: True if it was successful else False
        """
        try:
            await self._client.http.delete(endpoint=f"/users/@me/houses/{self.id}")
            return True

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to leave {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return False

    async def edit(self, **kwargs) -> bool:
        """
        Changes the houses data on Hiven.

        Available options: name, icon(base64)

        :return: True if the request was successful else False
        """
        try:
            for key, data in kwargs.items():
                if key in ['name']:
                    await self._client.http.patch(endpoint=f"/houses/{self.id}", json={key: data})
                    return True
                else:
                    raise NameError("The passed value does not exist in the House!")

        except Exception as e:
            keys = "".join(key + " " for key in kwargs.keys()) if kwargs != {} else ''
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed edit request of values '{keys}' in house {repr(self)}: \n"
                       f"{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return False

    async def create_invite(self, max_uses: int) -> typing.Optional[Invite]:
        """
        Creates an invite for the current house. 

        :param max_uses: Maximal uses for the invite code
        :return: The invite url if successful.
        """
        try:
            from . import Invite
            resp = await self._client.http.post(endpoint=f"/houses/{self.id}/invites", json={"max_uses": max_uses})
            raw_data = await resp.json()

            data = raw_data.get('data')
            data = Invite.format_obj_data(data)
            return Invite(data, self._client)

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to create invite for house '{self.name}' with id {self.id}: \n"
                       f"{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return None

    async def delete(self) -> typing.Optional[str]:
        """
        Deletes the house if permissions are sufficient!
        
        :return: The house ID if successful else None
        """
        try:
            await self._client.http.delete(f"/houses/{self.id}")
            return self.id

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to delete House {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            # TODO! Raise exception
            return None
