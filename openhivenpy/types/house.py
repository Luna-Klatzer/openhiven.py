# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
import types
import typing
import fastjsonschema

from . import HivenObject, check_valid
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError

# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Member, Room, Entity, Invite

logger = logging.getLogger(__name__)

__all__ = ['House', 'LazyHouse']


class LazyHouse(HivenObject):
    """
    Represents a Hiven House which can contain rooms and entities

    Note! This class is a lazy class and does not have every available data!

    Consider fetching for more data the regular house object with HivenClient.get_house()
    """
    schema = {
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
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._name = kwargs.get('name')
        self._icon = kwargs.get('icon')
        self._owner_id = kwargs.get('owner_id')
        self._rooms = kwargs.get('rooms')
        self._type = kwargs.get('type')

    def __str__(self):
        return self.name

    def get_cached_data(self) -> typing.Union[dict, None]:
        """ Fetches the most recent data from the cache based on the instance id """
        return self._client.storage['houses'][self.id]

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!
        Only exceptions are member objects which are unique in every house

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
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

        return data

    @classmethod
    def _insert_data(cls, data: dict, client):
        """
        Creates an instance of the LazyHouse Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed LazyHouse Instance
        """
        try:
            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            ) from e
        else:
            instance._client = client
            return instance

    @property
    def id(self) -> str:
        return getattr(self, '_id', None)

    @property
    def name(self) -> str:
        return getattr(self, '_name', None)

    @property
    def type(self) -> int:
        return getattr(self, '_type', None)

    @property
    def icon(self) -> typing.Union[str, None]:
        if getattr(self, '_icon', None):
            return "https://media.hiven.io/v1/houses/{}/icons/{}".format(self.id, self._icon)
        else:
            return None

    @property
    def owner_id(self) -> str:
        return getattr(self, '_owner_id', None)

    @property
    def rooms(self) -> list:
        return getattr(self, '_rooms', None)


class House(LazyHouse):
    """ Represents a Hiven House which can contain rooms and entities """
    schema = {
        'type': 'object',
        'properties': {
            **LazyHouse.schema['properties'],
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
        'required': [*LazyHouse.schema['required'], 'entities', 'members', 'roles']
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._roles = kwargs.get('roles')
        self._entities = kwargs.get('entities')
        self._default_permissions = kwargs.get('default_permissions')
        self._members = kwargs.get('members')
        self._client_member = kwargs.get('client_member')
        self._banner = kwargs.get('banner')
        self._owner = kwargs.get('owner')
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('banner', self.banner),
            ('owner_id', self.owner_id)
        ]
        return '<House {}>'.format(' '.join('%s=%s' % t for t in info))

    @classmethod
    @check_valid()
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
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

    @classmethod
    def _insert_data(cls, data: dict, client):
        """
        Creates an instance of the House Class with the passed data
        (Needs to be already validated/formed and populated with the wanted data -> objects should be ids)

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed House Instance
        """
        try:
            from . import Member
            instance = cls(**data)
            instance._client = client

            client_data = instance.get_cached_data()['members'][client.id]
            instance._client_member = Member._insert_data(client_data, client)
            instance._owner = utils.get(instance.members, id=instance.owner_id)
    
        except Exception as e:
            utils.log_traceback(
                msg=f"Traceback in function '{cls.__name__}' Validation:",
                suffix=f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            ) from e
        else:
            return instance

    @property
    def owner(self) -> Member:
        return getattr(self, '_owner', None)

    @property
    def client_member(self) -> Member:
        return getattr(self, '_client_member', None)

    @property
    def banner(self) -> str:
        return getattr(self, '_banner', None)

    @property
    def roles(self) -> list:
        return getattr(self, '_roles', None)

    @property
    def entities(self) -> typing.List[Entity]:
        return getattr(self, '_entities', None)

    @property
    def users(self) -> typing.List[Member]:
        return getattr(self, '_members', None)

    @property
    def members(self) -> typing.List[Member]:
        return getattr(self, '_members', None)

    @property
    def default_permissions(self) -> int:
        return self._default_permissions

    def get_member(self, member_id: int) -> typing.Union[Room, None]:
        """
        Fetches a member from the cache based on the id

        :returns: The Member Instance if it exists else returns None
        """
        try:
            from . import Member
            # TODO! Create new class when fetched
            cached_member = utils.get(self.members, id=member_id)
            if cached_member:
                return cached_member
            else:
                logger.warning(f"[HOUSE] Found no member with specified id={member_id} in {repr(self)}!")

            return None

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to get the member with id {member_id}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return None

    def get_room(self, room_id: int) -> typing.Union[Room, None]:
        """
        Fetches a room from the cache based on the id

        :returns: The Room Instance if it exists else returns None
        """
        try:
            from . import Room
            # TODO! Create new class when fetched
            cached_room = utils.get(self.rooms, id=room_id)
            if cached_room:
                return cached_room
            else:
                logger.warning(f"[HOUSE] Found no room with specified id={room_id} in the client cache!")

            return None
        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to get the room with id {room_id} in house {repr(self)}: \n"
                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    def get_entity(self, entity_id: int) -> typing.Union[Entity, None]:
        """
        Fetches a entity from the cache based on the id

        :returns: The Entity Instance if it exists else returns None
        """
        try:
            from . import Entity
            # TODO! Create new class when fetched
            cached_member = utils.get(self.members, id=entity_id)
            if cached_member:
                return cached_member
            else:
                logger.warning(f"[HOUSE] Found no member with specified id={entity_id} in {repr(self)}!")

            return None

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to get the member with id {entity_id}: \n{sys.exc_info()[0].__name__}: {e}")
            return None

    async def create_room(self, name: str, parent_entity_id: typing.Optional[int] = None) -> typing.Union[Room, None]:
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
            return Room._insert_data(data, self._client)

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to create room '{name}' in house {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return None

    async def create_entity(self, name: str) -> typing.Union[Entity, None]:
        """
        Creates a entity in the house with the specified name.

        :param name: The name of the new entity
        :returns: The newly created Entity Instance
        """
        try:
            resp = await self._client.http.post(
                endpoint=f"/houses/{self.id}/entities",
                json={'name': name, 'type': 1}
            )
            raw_data = await resp.json()

            data = raw_data.get('data')

            # Fetching all existing ids
            existing_entity_ids = [e.id for e in self.entities]
            for d in data:
                id_ = d.get('id')
                if id_ not in existing_entity_ids:
                    d = Entity.format_obj_data(d)
                    _entity = Entity._insert_data(d, self._client)
                    self._entities.append(_entity)
                    return _entity

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to create category '{name}' in house {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return None

    async def leave(self) -> bool:
        """
        Leaves the house
        
        :returns: True if it was successful else False
        """
        try:
            await self._client.http.delete(endpoint=f"/users/@me/houses/{self.id}")
            return True

        except Exception as e:
            utils.log_traceback(msg="[HOUSE] Traceback:",
                                suffix=f"Failed to leave {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
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
            utils.log_traceback(msg="[HOUSE] Traceback:",
                                suffix=f"Failed edit request of values '{keys}' in house {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def create_invite(self, max_uses: int) -> typing.Union[Invite, None]:
        """
        Creates an invite for the current house. 

        :param max_uses: Maximal uses for the invite code
        :return: The invite url if successful.
        """
        try:
            from . import Invite
            resp = await self._client.http.post(endpoint=f"/houses/{self.id}/invites", json={"max_uses": max_uses})
            raw_data = await resp.json()

            data = raw_data.get('data', {})
            data = Invite.format_obj_data(data)
            return Invite._insert_data(data, self._client)

        except Exception as e:
            utils.log_traceback(msg="[HOUSE] Traceback:",
                                suffix=f"Failed to create invite for house '{self.name}' with id {self.id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def delete(self) -> typing.Union[str, None]:
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
            return None
