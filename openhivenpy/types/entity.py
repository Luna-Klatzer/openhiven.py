"""
Entity File which implements the Hiven Entity type and its methods (endpoints)

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
from typing import Optional, List
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .hiven_type_schemas import get_compiled_validator, EntitySchema
from ..base_types import DataClassObject
from ..exceptions import InvalidPassedDataError
from ..utils import log_type_exception

if TYPE_CHECKING:
    from . import House, TextRoom
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Entity']


class Entity(DataClassObject):
    """ Represents a Hiven Entity inside a House which can contain Rooms """
    _json_schema: dict = EntitySchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('Entity')
    def __init__(self, data: dict, client: HivenClient):
        """
        Represents a Hiven Entity inside a House which can contain Rooms

        :param data: Data that should be used to create the object
        :param client: The HivenClient
        """
        super().__init__()
        self._type = data.get('type')
        self._position = data.get('position')
        self._resource_pointers = data.get('resource_pointers')
        self._name = data.get('name')
        self._id = data.get('id')
        self._house_id = data.get('house_id')
        self._house = data.get('house')
        self._client = client

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('position', self.position),
            ('type', self.type)
        ]
        return '<Entity {}>'.format(' '.join('%s=%s' % t for t in info))

    def get_cached_data(self) -> Optional[dict]:
        """
        Fetches the most recent data from the cache based on the instance id.

        If updated while the object exists, the data might differentiate, due
        to the object not being updated unlike the cache.
        """
        return self._client.storage['entities'].get(self.id)

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be 
        required for the creation of an instance.


        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a 
         new class instance
        """
        if not data.get('house_id') and data.get('house'):
            house = data.pop('house')
            if type(house) is dict:
                house_id = house.get('id')
            elif isinstance(house, DataClassObject):
                house_id = getattr(house, 'id', None)
            else:
                house_id = None

            if house_id is None:
                raise InvalidPassedDataError(
                    "The passed house is not in the correct format!",
                    data=data
                )
            else:
                data['house_id'] = house_id

        data['house'] = data.get('house_id')
        data = cls.validate(data)
        return data

    @property
    def type(self) -> Optional[int]:
        """ Type of the entity """
        return getattr(self, '_type', None)

    @property
    def resource_pointers(self) -> Optional[List[TextRoom, dict]]:
        """
        Objects contained inside the entity. If dict is returned it's a type
        that is not yet included in the lib
        """
        from . import TextRoom
        if type(self._resource_pointers) is list \
                and len(self._resource_pointers) > 0:
            resources_created = False
            for _ in self._resource_pointers:
                if type(_) is not dict:
                    resources_created = True

            if not resources_created:
                resource_pointers = []
                for d in self._resource_pointers:
                    if d['resource_type'] == "room":
                        data = self._client.storage['rooms']['house'][d['resource_id']]
                        resource_pointers.append(TextRoom(data, client=self._client))
                    else:
                        resource_pointers.append(d)

                self._resource_pointers = resource_pointers
            return self._resource_pointers

        else:
            return None

    @property
    def name(self) -> Optional[str]:
        """ Name of the entity """
        return getattr(self, '_name', None)

    @property
    def id(self) -> Optional[str]:
        """ ID of the entity """
        return getattr(self, '_id', None)

    @property
    def house_id(self) -> Optional[str]:
        """ ID of the House parent of the Entity """
        return getattr(self, '_house_id', None)

    @property
    def position(self) -> Optional[int]:
        """ Position on the sidebar of the Room """
        return getattr(self, '_position', None)

    @property
    def house(self) -> Optional[House]:
        """ House object of the entity """
        from . import House
        if type(self._house) is str:
            house_id = self._house
        elif type(self.house_id) is str:
            house_id = self.house_id
        else:
            house_id = None

        if house_id:
            data = self._client.storage['houses'].get(house_id)
            if data:
                self._house = House(data=data, client=self._client)
                return self._house
            else:
                return None

        elif type(self._house) is House:
            return self._house
        else:
            return None
