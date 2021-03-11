"""House Module for Hiven House Objects"""
import logging
import sys
import types
import typing
import fastjsonschema

from . import HivenObject, check_valid
from . import invite
from . import entity
from . import member
from . import room
from .. import utils
from ..exceptions import InvalidPassedDataError, InitializationError, HTTPResponseError, HTTPReceivedNoDataError
logger = logging.getLogger(__name__)

__all__ = ['House', 'LazyHouse']


class LazyHouse(HivenObject):
    """
    Low-Level Data Class for a Hiven House

    Note! This class is a lazy class and does not have every available data!

    Consider fetching for more data the regular house object with utils.get()
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
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!
        Only excluded for member objects which are unique in every house

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        if type(data.get('members')) is list:
            data['members'] = {m['user_id'] if m.get('user_id') else m.get('user').get('id'):
                               utils.update_and_return(m, {
                                   'user': m['user_id'] if m.get('user_id') else m.get('user').get('id')
                               })
                               for m in data['members']}
        if type(data.get('rooms')) is list:
            data['rooms'] = [i['id'] for i in data['rooms']]
        if type(data.get('entities')) is list:
            data['entities'] = [i['id'] for i in data['entities']]

        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the LazyHouse Class with the passed data

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
    """ Data Class for a Hiven House """
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
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        data = cls.validate(data)
        data = LazyHouse.form_object(data)
        data['owner'] = utils.convert_value(int, data.get('owner_id'))
        data['default_permissions'] = data.get('default_permissions')
        return data

    @classmethod
    async def create_from_dict(cls, data: dict, client):
        """
        Creates an instance of the House Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed House Instance
        """
        try:
            instance = cls(**data)
            instance._client_member = member.Member.create_from_dict(
                cls.raw['members'][client.id], client
            )
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
            instance._client = client
            return instance

    @property
    def owner(self) -> member.Member:
        return getattr(self, '_owner', None)

    @property
    def client_member(self) -> member.Member:
        return getattr(self, '_client_member', None)

    @property
    def banner(self) -> list:
        return getattr(self, '_banner', None)

    @property
    def roles(self) -> list:
        return getattr(self, '_roles', None)

    @property
    def entities(self) -> list:
        return getattr(self, '_entities', None)

    @property
    def users(self) -> list:
        return getattr(self, '_members', None)

    @property
    def members(self) -> list:
        return getattr(self, '_members', None)

    @property
    def default_permissions(self) -> int:
        return self._default_permissions

    def get_member(self, member_id: int):
        """
        Fetches a member from the cache based on the id

        :returns: The Member Instance if it exists else returns None
        """
        try:
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
            return False

    def get_room(self, room_id: int):
        """
        Fetches a room from the cache based on the id

        :returns: The Room Instance if it exists else returns None
        """
        try:
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
            return False

    def get_entity(self, entity_id: int):
        """
        Fetches a entity from the cache based on the id

        :returns: The Entity Instance if it exists else returns None
        """
        try:
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
            return False

    async def create_room(self, name: str, parent_entity_id: typing.Optional[int] = None):
        """
        Creates a Room in the house with the specified name. 
        
        :return: A Room Instance for the Hiven Room that was created if successful else None
        """
        try:
            default_entity = utils.get(self.entities, name="Rooms")
            json = {
                'name': name,
                'parent_entity_id': parent_entity_id if parent_entity_id else default_entity.id
            }

            # Creating the room using the api
            resp = await self._client.http.post(f"/houses/{self._id}/rooms", json=json)

            if resp.status < 300:
                data = (await resp.json()).get('data')
                if data:
                    _room = await room.Room.create_from_dict(data, self._client)

                    return _room
                else:
                    raise HTTPReceivedNoDataError()
            else:
                raise HTTPResponseError("Unknown! See HTTP Logs!")

        except Exception as e:
            utils.log_traceback(
                msg="[HOUSE] Traceback:",
                suffix=f"Failed to create room '{name}' in house {repr(self)}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            return None

    # TODO! Delete Room!

    async def create_entity(self, name: str) -> typing.Union[entity.Entity, None]:
        """
        Creates a entity in the house with the specified name.

        :param name: The name of the new entity
        :returns: The newly created Entity Instance
        """
        try:
            json = {'name': name, 'type': 1}
            resp = await self._client.http.post(endpoint=f"/houses/{self.id}/entities", json=json)

            if resp.status < 300:
                data = (await resp.json()).get('data')
                if data:
                    # Fetching all existing ids
                    existing_entity_ids = [e.id for e in self.entities]
                    for d in data:
                        id_ = utils.convert_value(int, d.get('id'))
                        # Returning the new entity
                        if id_ not in existing_entity_ids:
                            _entity = await entity.Entity.create_from_dict(d, self._client)
                            self._entities.append(_entity)
                            return _entity
                    raise InitializationError(f"Failed to initialise the Entity Instance! Data: {data}")
                else:
                    raise HTTPReceivedNoDataError()
            else:
                raise HTTPResponseError("Unknown! See HTTP Logs!")

        except Exception as e:
            utils.log_traceback(msg="[HOUSE] Traceback:",
                                suffix=f"Failed to create category '{name}' in house {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def leave(self) -> bool:
        """
        Leaves the house
        
        :returns: True if it was successful else False
        """
        try:
            resp = await self._client.http.delete(endpoint=f"/users/@me/houses/{self.id}")

            if resp.status < 300:
                return True
            else:
                raise HTTPResponseError("Unknown! See HTTP Logs!")

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
                    resp = await self._client.http.patch(endpoint=f"/houses/{self.id}", json={key: data})

                    if resp.status < 300:
                        return True
                    else:
                        raise HTTPResponseError("Unknown! See HTTP Logs!")
                else:
                    raise NameError("The passed value does not exist in the House!")

        except Exception as e:
            keys = "".join(key + " " for key in kwargs.keys()) if kwargs != {} else ''
            utils.log_traceback(msg="[HOUSE] Traceback:",
                                suffix=f"Failed edit request of values '{keys}' in house {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def create_invite(self, max_uses: int) -> typing.Union[invite.Invite, None]:
        """
        Creates an invite for the current house. 

        :param max_uses: Maximal uses for the invite code
        :return: The invite url if successful.
        """
        try:
            resp = await self._client.http.post(endpoint=f"/houses/{self.id}/invites", json={"max_uses": max_uses})

            if resp.status < 300:
                raw_data = await resp.json()
                data = raw_data.get('data', {})

                if data:
                    return await invite.Invite.create_from_dict(data, self._client)
                else:
                    raise HTTPReceivedNoDataError()
            else:
                raise HTTPResponseError("Unknown! See HTTP Logs!")

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
            resp = await self._client.http.delete(f"/houses/{self.id}")

            if resp.status < 300:
                return self.id
            else:
                return None

        except Exception as e:
            utils.log_traceback(msg="[HOUSE] Traceback:",
                                suffix=f"Failed to delete House {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None
