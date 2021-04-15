import logging
import sys

from .. import utils
from .. import types
from ..exceptions import InitializationError

__all__ = ['ClientCache']

logger = logging.getLogger(__name__)


class ClientCache(dict):
    """
    Client Cache Class used for storing all data of the Client. Emulates a dictionary and contains additional
    functions to interact with the Client cache more easily and use functions for better readability.
    """
    def __init__(self, log_ws_output: bool, *args, **kwargs):
        super(ClientCache, self).__init__(*args, **kwargs)
        self.update({
            'token': 'undefined',
            'log_ws_output': log_ws_output,
            'client_user': dict(),
            'houses': dict(),
            'users': dict(),
            'rooms': {
                'private': {
                    'single': dict(),
                    'multi': dict()
                },
                'house': dict()
            },
            'entities': dict(),
            'relationships': dict(),
            'house_memberships': dict(),
            'house_ids': list(),
            'settings': dict(),
            'read_state': dict()
        })

    def check_if_initialised(self):
        if self.get('client_user', None) is not None:
            return True
        else:
            raise ValueError("Data Updates require a initialised Hiven Client!")

    def update_all(self, data: dict) -> dict:
        """
        Updates based on the data the main cache for the Client

        :return: The updated cache itself
        """
        self['house_memberships'] = data.get('house_memberships', {})
        self['house_ids'] = data.get('house_ids', [])
        self['settings'] = data.get('settings', {})
        self['read_state'] = data.get('read_state', {})

        for r in data.get('private_rooms', []):
            self.add_or_update_private_room(r)

        for key, data in data.get('relationships', []).items():
            self.add_or_update_relationship(data)

        return self

    def update_client_user(self, data: dict) -> dict:
        """
        Updating the Client Cache Data from the passed data dict

        :return: The validated data using `format_obj_data` of the User class
        """
        data = dict(data)
        client_user = types.User.format_obj_data(data)
        self['client_user'].update(client_user)

        if self['users'].get(data['id']) is not None:
            self['users'][data['id']].update(client_user)
        else:
            self['users'][data['id']] = client_user

        return client_user

    def add_or_update_house(self, data: dict) -> dict:
        """
        Adds or Updates a house to the cache and updates the storage appropriately

        :return: The validated data using `format_obj_data` of the House class
        """
        self.check_if_initialised()
        try:
            data = dict(data)
            id_ = data['id']
            for room in data['rooms']:
                room['house_id'] = id_
                room = types.Room.format_obj_data(room)
                self.add_or_update_room(room)

            for member in data['members']:
                member['house_id'] = id_
                user = types.User.format_obj_data(member['user'])
                self.add_or_update_user(user)

            for entity in data['entities']:
                entity['house_id'] = id_
                entity = types.Entity.format_obj_data(entity)
                self.add_or_update_entity(entity)

            data = types.House.format_obj_data(data)
            data['client_member'] = data['members'][self['client_user']['id']]
            if self['houses'].get(id_) is None:
                self['houses'][id_] = data
            else:
                self['houses'][id_].update(data)

            return data

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_house: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}"
            )
            raise InitializationError("Failed to update the cache due to an exception occurring") from e

    def add_or_update_user(self, data: dict) -> dict:
        """
        Adds or Updates a user to the cache and updates the storage appropriately

        :return: The validated data using `format_obj_data` of the User class
        """
        self.check_if_initialised()
        try:
            data = dict(data)
            id_ = data['id']
            data = types.User.format_obj_data(data)
            if self['users'].get(id_) is None:
                self['users'][id_] = data
            else:
                self['users'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_user: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError("Failed to update the cache due to an exception occurring") from e

    def add_or_update_room(self, data: dict) -> dict:
        """
        Adds or Updates a room to the cache and updates the storage appropriately

        :return: The validated data using `format_obj_data` of the Room class
        """
        self.check_if_initialised()
        try:
            data = dict(data)
            id_ = data['id']
            data = types.Room.format_obj_data(data)
            if self['rooms']['house'].get(id_) is None:
                self['rooms']['house'][id_] = data
            else:
                self['rooms']['house'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_room: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}"
            )
            raise InitializationError("Failed to update the cache due to an exception occurring") from e

    def add_or_update_entity(self, data: dict) -> dict:
        """
        Adds or Updates a entity to the cache and updates the storage appropriately

        :return: The validated data using `format_obj_data` of the Entity class
        """
        self.check_if_initialised()
        try:
            data = dict(data)
            id_ = data['id']
            data = types.Entity.format_obj_data(data)
            if self['entities'].get(id_) is None:
                self['entities'][id_] = data
            else:
                self['entities'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_room: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError("Failed to update the cache due to an exception occurring") from e

    def add_or_update_private_room(self, data: dict) -> dict:
        """
        Adds or Updates a private room to the cache and updates the storage appropriately

        :return: The validated data using `format_obj_data` of the Private_*Room class
        """
        self.check_if_initialised()
        try:
            data = dict(data)
            id_ = data['id']
            if int(data['type']) == 1:
                data = types.PrivateRoom.format_obj_data(data)
                if self['rooms']['private']['single'].get(id_) is None:
                    data['type'] = 'single'
                    self['rooms']['private']['single'][id_] = data
                else:
                    self['rooms']['private']['single'][id_].update(data)

            elif int(data['type']) == 2:
                data = types.PrivateGroupRoom.format_obj_data(data)
                if self['rooms']['private']['multi'].get(id_) is None:
                    data['type'] = 'single'
                    self['rooms']['private']['multi'][id_] = data
                else:
                    self['rooms']['private']['multi'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_room: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError("Failed to update the cache due to an exception occurring") from e

    def add_or_update_relationship(self, data: dict) -> dict:
        """
        Adds or Updates a client relationship to the cache and updates the storage appropriately

        :return: The validated data using `format_obj_data` of the Relationship class
        """
        self.check_if_initialised()
        try:
            data = dict(data)
            id_ = data['user_id']
            data = types.Relationship.format_obj_data(data)
            if self['relationships'].get(id_) is None:
                self['relationships'][id_] = data
            else:
                self['relationships'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_room: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise InitializationError("Failed to update the cache due to an exception occurring") from e
