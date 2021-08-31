"""
File containing the ClientCache class, which manages data and updates

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import logging
import sys
# Using deepcopy instead of standard .copy() from python since regular dict()
# or dict.copy() would not duplicate its iterable properties as well and the
# keys for iterables would point to the same object, which results in that
# changes to those iterables are applied to all copied dictionaries that were
# created using dict() or copy().
from copy import deepcopy
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .. import types
from .. import utils
from ..base_types import HivenObject
from ..exceptions import InitializationError

if TYPE_CHECKING:
    from .. import HivenClient

__all__ = ['ClientCache']

logger = logging.getLogger(__name__)


def _create_default_dict(log_websocket: bool) -> dict:
    """ Creates the default dictionary format used inside the cache """
    return {
        'token': 'undefined',
        'log_websocket': log_websocket,
        'client_user': dict(),
        'houses': dict(),
        'users': dict(),
        'rooms': {
            'private': {
                'single': dict(),
                'group': dict()
            },
            'house': dict()
        },
        'entities': dict(),
        'relationships': dict(),
        'house_ids': list(),
        'settings': dict(),
        'init_read_state': dict()
    }


class ClientCache(dict, HivenObject):
    """
    Client Cache Class used for storing all data of the Client. Emulates a
    dictionary and contains additional functions to interact with the Client
    cache more easily and use functions for better readability.
    """

    def __init__(self, client: HivenClient, log_websocket: bool, **kwargs):
        super(ClientCache, self).__init__(**kwargs)
        self.client = client
        self.update(
            # Updating the passed dict as well to avoid data being overwritten
            # that were passed with args or kwargs
            utils.update_and_return(
                _create_default_dict(log_websocket), **kwargs
            )
        )

    def closing_cleanup(self) -> None:
        """
        Cleans all remaining data after the client exited.

        Not supposed to be called outside of the intended HivenClient.close()
        method!
        """
        self.update(_create_default_dict(self['log_websocket']))
        self['client_user'] = {}
        self.init_client_user_obj()

    def init_client_user_obj(self) -> types.User:
        """ Initialises the client user based on the cached data """
        return types.User(self['client_user'], self.client)

    def check_if_initialised(self) -> bool:
        """ Checks whether the client has initialised """
        if self.get('client_user'):
            return True
        else:
            raise ValueError("Updates require an initialised Hiven Client!")

    def update_primary_data(self, item_data: dict) -> None:
        """
        Updates in the cache the following data:
         - List of all House Memberships
         - List of all House Ids
         - The Client settings of the user
         - The read state of messages
         - All open Private Rooms
         - All Relationships of the user
        """
        data = deepcopy(item_data)
        self['house_ids'] = data.get('house_ids', [])
        self['settings'] = data.get('settings', {})
        self['init_read_state'] = data.get('read_state', {})
        self.update_client_user(data.get('user'))

        for r in data.get('private_rooms', []):
            self.add_or_update_private_room(r)

        for key, data in data.get('relationships', []).items():
            self.add_or_update_relationship(data)

    def update_client_user(self, item_data: dict) -> dict:
        """
        Updating the Client Cache Data from the passed data dict

        :return: The validated data using `format_obj_data` of the User class
        """
        data = deepcopy(item_data)
        client_user = types.User.format_obj_data(data)
        self['client_user'].update(client_user)

        if self['users'].get(data['id']) is not None:
            self['users'][data['id']].update(client_user)
        else:
            self['users'][data['id']] = client_user

        return client_user

    def add_or_update_house(self, item_data: dict) -> dict:
        """
        Adds or Updates a house to the cache and updates the storage
        appropriately

        :return: The validated data using `format_obj_data` of the House class
        """
        self.check_if_initialised()
        try:
            data = deepcopy(item_data)
            id_ = data['id']
            for room in data['rooms']:
                room['house_id'] = id_
                room = types.TextRoom.format_obj_data(room)
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
                # Checking whether id does not already exist
                # On init house_ids is already populated using the event
                # INIT_STATE, though HOUSE_JOIN triggers this function, meaning
                # we have to avoid creating duplicates on initialisation
                if id_ not in self['house_ids']:
                    self['house_ids'].append(id_)
                self['houses'][id_] = data
            else:
                self['houses'][id_].update(data)

            return data

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to add a new house to the Client cache:",
                exc_info=sys.exc_info()
            )
            raise InitializationError(
                "Failed to update the cache due to an exception occurring"
            ) from e

    def remove_house(self, _id: str) -> None:
        """ Removes a house from the cache """
        self.check_if_initialised()
        del self['houses'][_id]

        self['house_ids']: list
        self['house_ids'].remove(_id)

    def add_or_update_user(self, item_data: dict) -> dict:
        """
        Adds or Updates a user to the cache and updates the storage
        appropriately

        :return: The validated data using `format_obj_data` of the User class
        """
        self.check_if_initialised()
        try:
            data = deepcopy(item_data)
            id_ = data['id']
            data = types.User.format_obj_data(data)

            if id_ == self['client_user'].get('id'):
                self.update_client_user(data)

            if self['users'].get(id_) is None:
                self['users'][id_] = data
            else:
                self['users'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to add a new house to the Client cache:",
                exc_info=sys.exc_info()
            )
            raise InitializationError(
                "Failed to update the cache due to an exception occurring"
            ) from e

    def remove_user(self, _id: str) -> None:
        """ Removes a user from the cache """
        self.check_if_initialised()
        del self['users'][_id]

    def add_or_update_room(self, item_data: dict) -> dict:
        """
        Adds or Updates a room to the cache and updates the storage
        appropriately

        :return: The validated data using `format_obj_data` of the Room class
        """
        self.check_if_initialised()
        try:
            data = deepcopy(item_data)
            id_ = data['id']
            data = types.TextRoom.format_obj_data(data)
            if self['rooms']['house'].get(id_) is None:
                self['rooms']['house'][id_] = data
            else:
                self['rooms']['house'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to add a new house to the Client cache:",
                exc_info=sys.exc_info()
            )
            raise InitializationError(
                "Failed to update the cache due to an exception occurring"
            ) from e

    def remove_room(self, _id: str) -> None:
        """ Removes a room from the cache """
        self.check_if_initialised()
        del self['rooms']['house'][_id]

    def add_or_update_entity(self, item_data: dict) -> dict:
        """
        Adds or Updates a entity to the cache and updates the storage
        appropriately

        :return: The validated data using `format_obj_data` of the Entity class
        """
        self.check_if_initialised()
        try:
            data = deepcopy(item_data)
            id_ = data['id']
            data = types.Entity.format_obj_data(data)
            if self['entities'].get(id_) is None:
                self['entities'][id_] = data
            else:
                self['entities'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to add a new house to the Client cache:",
                exc_info=sys.exc_info()
            )
            raise InitializationError(
                "Failed to update the cache due to an exception occurring"
            ) from e

    def remove_entity(self, _id: str) -> None:
        """ Removes an entity from the cache """
        self.check_if_initialised()
        del self['entities'][_id]

    def add_or_update_private_room(self, item_data: dict) -> dict:
        """
        Adds or Updates a private room to the cache and updates the storage
        appropriately

        :return: The validated data using `format_obj_data` of the
        Private_*Room class
        """
        self.check_if_initialised()
        try:
            data = deepcopy(item_data)
            id_ = data['id']
            if int(data['type']) == 1:
                types.PrivateRoom.format_obj_data(data)
                if self['rooms']['private']['single'].get(id_) is None:
                    self['rooms']['private']['single'][id_] = data
                else:
                    self['rooms']['private']['single'][id_].update(data)

            elif int(data['type']) == 2:
                types.PrivateGroupRoom.format_obj_data(data)
                if self['rooms']['private']['group'].get(id_) is None:
                    self['rooms']['private']['group'][id_] = data
                else:
                    self['rooms']['private']['group'][id_].update(data)
            else:
                raise ValueError("Data does not contain correct type-id")
            return data

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to add a new house to the Client cache:",
                exc_info=sys.exc_info()
            )
            raise InitializationError(
                "Failed to update the cache due to an exception occurring"
            ) from e

    def remove_private_room(self, _id: str) -> None:
        """ Removes a private-room from the cache """
        self.check_if_initialised()

        for i in self['rooms']['private']['group']:
            if i.get('id') == _id:
                del self['rooms']['private']['group'][_id]
                return

        for i in self['rooms']['private']['single']:
            if i.get('id') == _id:
                del self['rooms']['private']['single'][_id]

    def add_or_update_relationship(self, item_data: dict) -> dict:
        """
        Adds or Updates a client relationship to the cache and updates the
        storage appropriately

        :return: The validated data using `format_obj_data` of the Relationship
         class
        """
        self.check_if_initialised()
        try:
            data = deepcopy(item_data)
            id_ = data['user_id']

            if data.get('user'):
                self.add_or_update_user(data['user'])

            data = types.Relationship.format_obj_data(data)
            if self['relationships'].get(id_) is None:
                self['relationships'][id_] = data
            else:
                self['relationships'][id_].update(data)
            return data

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to add a new house to the Client cache:",
                exc_info=sys.exc_info()
            )
            raise InitializationError(
                "Failed to update the cache due to an exception occurring"
            ) from e

    def remove_relationship(self, _id: str) -> None:
        """ Removes a relationship from the cache """
        self.check_if_initialised()
        del self['relationships'][_id]
