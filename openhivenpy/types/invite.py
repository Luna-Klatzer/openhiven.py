"""
Invite File which implements the Hiven Invite type

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
from typing import Optional
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from . import House
from .hiven_type_schemas import InviteSchema, get_compiled_validator
from ..base_types import DataClassObject
from ..exceptions import InvalidPassedDataError
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['Invite']


class Invite(DataClassObject):
    """ Represents an Invite to a Hiven House """
    _json_schema: dict = InviteSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('Invite')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._code = data.get('code')
        self._url = data.get('url')
        self._created_at = data.get('created_at')
        self._house_id = data.get('house_id')
        self._max_age = data.get('max_age')
        self._max_uses = data.get('max_uses')
        self._type = data.get('type')
        self._house = data.get('house')
        self._house_members = data.get('house_members')
        self._client = client

    def __repr__(self) -> str:
        info = [
            ('code', self.code),
            ('url', self.url),
            ('created_at', self.created_at),
            ('house_id', self.house_id),
            ('type', self.type),
            ('max_age', self.max_age),
            ('max_uses', self.max_uses),
        ]
        return '<Invite {}>'.format(' '.join('%s=%s' % t for t in info))

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
        if data.get('invite') is not None:
            invite = data.get('invite')
        else:
            invite = data
        data['code'] = invite.get('code')
        data['url'] = "https://hiven.house/{}".format(data['code'])
        data['created_at'] = invite.get('created_at')
        data['max_age'] = invite.get('max_age')
        data['max_uses'] = invite.get('max_uses')
        data['type'] = invite.get('type')
        data['house_members'] = data.get('counts', {}).get('house_members')

        if not invite.get('house_id') and invite.get('house'):
            house = invite.pop('house')
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

        data['type'] = int(data['type'])
        data['house'] = data.get('house_id')
        data = cls.validate(data)
        return data

    @property
    def code(self) -> Optional[int]:
        return getattr(self, '_code', None)

    @property
    def url(self) -> Optional[str]:
        return getattr(self, '_url', None)

    @property
    def house_id(self) -> Optional[str]:
        return getattr(self, '_house_id', None)

    @property
    def max_age(self) -> Optional[int]:
        return getattr(self, '_max_age', None)

    @property
    def max_uses(self) -> Optional[int]:
        return getattr(self, '_max_uses', None)

    @property
    def type(self) -> Optional[int]:
        return getattr(self, '_type', None)

    @property
    def house(self) -> Optional[House]:
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

    @property
    def house_members(self) -> Optional[int]:
        return getattr(self, '_house_members', None)

    @property
    def created_at(self) -> Optional[str]:
        return getattr(self, '_created_at', None)
