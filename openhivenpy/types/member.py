"""
Member File which implements the Hiven Member type and its methods
(endpoints)

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
from typing import Optional, List
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .hiven_type_schemas import MemberSchema, get_compiled_validator
from .user import User
from .. import utils
from ..base_types import DataClassObject
from ..exceptions import (HTTPForbiddenError,
                          InvalidPassedDataError)
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient
    from . import House

logger = logging.getLogger(__name__)

__all__ = ['Member']


class Member(User):
    """
    Represents a House Member on Hiven which contains the Hiven User, role-data
    and member-data
    """
    _json_schema: dict = MemberSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('Member')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__(data.get('user'), client)
        data = {**data.get('user'), **data}
        self._user_id = data.get('user_id')
        self._house_id = data.get('house_id')
        self._joined_at = data.get('joined_at')
        self._roles = data.get('roles')
        self._house = data.get('house')

    def __repr__(self) -> str:
        info = [
            ('username', self.username),
            ('name', self.name),
            ('id', self.id),
            ('icon', self.icon),
            ('header', self.header),
            ('bot', self.bot),
            ('house_id', self.house_id),
            ('joined_house_at', self.joined_house_at)
        ]
        return '<Member {}>'.format(' '.join('%s=%s' % t for t in info))

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
                    "The passed house is not in the correct format!", data=data
                )
            else:
                data['house_id'] = house_id

        elif not data.get('house_id') and not data.get('house'):
            raise InvalidPassedDataError(
                "house_id and house missing from required data", data=data
            )

        data['house'] = data.get('house_id')
        data = cls.validate(data)
        return data

    @property
    def id(self) -> Optional[str]:
        """ User-ID of the member. Alias for user_id """
        return self.user_id

    @property
    def user_id(self) -> Optional[str]:
        """ User-ID of the member """
        return getattr(self, '_user_id', None)

    @property
    def joined_house_at(self) -> Optional[str]:
        """ Joined at date (unix-timestamp probably). Alias for joined_at """
        return self.joined_at

    @property
    def joined_at(self) -> Optional[str]:
        """ Joined at date (unix-timestamp probably) """
        return getattr(self, '_joined_at', None)

    @property
    def house(self) -> Optional[House]:
        """ Parent House object instance of this class """
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
    def house_id(self) -> Optional[str]:
        """ Returns the ID of the parent House """
        return getattr(self, '_house_id', None)

    @property
    def roles(self) -> Optional[List[dict]]:
        """ Returns the roles of the Member """
        return getattr(self, '_roles', None)

    async def kick(self) -> bool:
        """
        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise
        `HivenException.Forbidden`
            
        :return: True if the request was successful
        :raises Forbidden: If the request failed to execute
        """
        try:
            resp = await self._client.http.delete(
                f"/{self._house_id}/members/{self._user_id}"
            )
            if not resp.status < 300:
                raise HTTPForbiddenError()
            else:
                return True
        except HTTPForbiddenError:
            raise

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to kick the member due to an exception "
                      "occurring:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return False
