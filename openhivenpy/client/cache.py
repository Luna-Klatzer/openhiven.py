import logging
import sys

from .. import utils

__all__ = ['ClientCache']

logger = logging.getLogger(__name__)


class ClientCache(dict):
    """
    Client Cache Class used for storing all data of the Client. Emulates a dictionary and contains additional
    functions to interact with the Client cache more easily and use functions for better readability.
    """
    def __init__(self, token: str, log_ws_output: bool, *args, **kwargs):
        super(ClientCache, self).__init__(*args, **kwargs)
        self['token'] = token
        self['log_ws_output'] = log_ws_output
        self['scope'] = {
            'houses': {},
            'users': {},
            'rooms': {
                'private': {
                    'single': {},
                    'multi': {}
                },
                'house': {}
            },
            'relationships': {},
            'house_memberships': {}
        }
        self['house_ids'] = []
        self['settings'] = {}
        self['read_state'] = {}
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
            self['scope']['users'][data['id']] = self['client_user']
        return self['client_user']

    def add_house(self, data: dict):
        """ Adds a new house to the cache and updates the storage appropriately"""
        try:
            self['scope']['houses'][data['id']] = data
            for room in data['rooms']:
                self['scope']['rooms']['house'][room['id']] = room

            for member in data['members']:
                if self['scope']['users'].get(member['user']['id']) is None:
                    self['scope']['users'][member['user']['id']] = member['user']

            return

        except Exception as e:
            utils.log_traceback(
                msg="[CLIENTCACHE] Traceback in 'add_house()': ",
                suffix=f"Failed to add a new house to the Client cache: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise
