import logging
import sys

from .. import utils
from .. import types

__all__ = ['ClientCache']

logger = logging.getLogger(__name__)


class ClientCache(dict):
    """
    Client Cache Class used for storing all data of the Client. Emulates a dictionary and contains additional
    functions to interact with the Client cache more easily and use functions for better readability.
    """

    def __init__(self, token: str, log_ws_output: bool, *args, **kwargs):
        super(ClientCache, self).__init__(*args, **kwargs)
        self.update({
            'token': token,
            'log_ws_output': log_ws_output,
            'houses': dict(),
            'users': dict(),
            'rooms': {
                'private': {
                    'single': dict(),
                    'multi': dict()
                },
                'house': dict()
            },
            'relationships': dict(),
            'house_memberships': dict(),
            'house_ids': list(),
            'settings': dict(),
            'read_state': dict()
        })
        self['client_user'] = self.update_client_user({})

    def update_client_user(self, data: dict):
        """ Updating the Client Cache Data from the passed data dict """
        self['client_user'] = {
            "id": data.get('id', None),
            "name": data.get('name', None),
            "username": data.get('username', None),
            "icon": data.get('icon', None),
            "header": data.get('header', None),
            "user_flags": data.get('user_flags', None),
            "bot": data.get('bot', None),
            "location": data.get('location', None),
            "website": data.get('website', None),
            "bio": data.get('bio', None),
            "email": data.get('email', None),
            "email_verified": data.get('email_verified', None),
            "mfa_enabled": data.get('mfa_enabled', None)
        }
        if self['client_user'].get('id') is not None:
            self['users'][data['id']] = self['client_user']
        return self['client_user']

    def add_or_update_house(self, data: dict):
        """ Adds a new house to the cache and updates the storage appropriately """
        try:
            self['houses'][data['id']] = data
            for room in data['rooms']:
                self['rooms']['house'][room['id']] = room

            for member in data['members']:
                self.add_or_update_user(member['user'])

            return

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_house: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise

    def add_or_update_user(self, data: dict):
        """ Adds a new user to the cache and updates the storage appropriately """
        try:
            id_ = data['id']
            data = types.User.form_object(data)
            if self['users'].get(id_) is None:
                self['users'][id_] = data
            else:
                self['users'][id_].update(data)
            return

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_user: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise

    def add_or_update_room(self, data: dict):
        """ Adds a new room to the cache and updates the storage appropriately """
        try:
            id_ = data['id']
            data = types.Room.form_object(data)
            if self['rooms']['house'].get(id_) is None:
                self['rooms']['house'][id_] = data
            else:
                self['rooms']['house'][id_].update(data)
            return

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_room: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise

    def add_or_update_private_room(self, data: dict):
        """ Adds a new private room to the cache and updates the storage appropriately """
        try:
            id_ = data['id']
            if int(data['type']) == 1:
                data = types.PrivateRoom.form_object(data)
                if self['rooms']['private']['single'].get(id_) is None:
                    data['type'] = 'single'
                    self['rooms']['private']['single'][id_] = data
                else:
                    self['rooms']['private']['single'][id_].update(data)

            elif int(data['type']) == 2:
                data = types.PrivateGroupRoom.form_object(data)
                if self['rooms']['private']['multi'].get(id_) is None:
                    data['type'] = 'single'
                    self['rooms']['private']['multi'][id_] = data
                else:
                    self['rooms']['private']['multi'][id_].update(data)

            return

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in add_or_update_room: ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise
