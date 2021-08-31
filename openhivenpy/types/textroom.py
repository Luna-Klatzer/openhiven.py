"""
TextRoom File which implements the Hiven TextRoom and its methods (endpoints)

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

import asyncio
import logging
import sys
from typing import Optional, List
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .hiven_type_schemas import TextRoomSchema, get_compiled_validator
from .house import House
from .message import Message
from .. import utils
from ..base_types import DataClassObject
from ..exceptions import InvalidPassedDataError
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['TextRoom']


class TextRoom(DataClassObject):
    """
    Represents a Hiven Room inside a House

    ---

    Possible Types:
            0 - Text

            1 - Portal
    """
    _json_schema: dict = TextRoomSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('TextRoom')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._id = data.get('id')
        self._name = data.get('name')
        self._house_id = data.get('house_id')
        self._position = data.get('position')
        self._type = data.get('type')
        self._emoji = data.get('emoji')
        self._description = data.get('description')
        self._last_message_id = data.get('last_message_id')
        self._house = data.get('house')
        self._client = client

    def __repr__(self) -> str:
        info = [
            ('name', self.name),
            ('id', self.id),
            ('house_id', self.house_id),
            ('position', self.position),
            ('type', self.type),
            ('emoji', self.emoji),
            ('description', self.description)
        ]
        return str('<Room {}>'.format(' '.join('%s=%s' % t for t in info)))

    def get_cached_data(self) -> Optional[dict]:
        """
        Fetches the most recent data from the cache based on the instance id.

        If updated while the object exists, the data might differentiate, due
        to the object not being updated unlike the cache.
        """
        return self._client.storage['rooms']['house'][self.id]

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be
        required for the creation of an instance.

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

        data['house'] = data['house_id']
        data = cls.validate(data)
        return data

    @property
    def id(self) -> Optional[str]:
        """ ID of the Room """
        return getattr(self, '_id', None)

    @property
    def name(self) -> Optional[str]:
        """ Name of the Room """
        return getattr(self, '_name', None)

    @property
    def house_id(self) -> Optional[str]:
        """ The ID of the parent house """
        return getattr(self, '_house_id', None)

    @property
    def house(self) -> Optional[House]:
        """ The parent house object """
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
    def position(self) -> Optional[int]:
        """ Position on the sidebar of the Room """
        return getattr(self, '_position', None)

    @property
    def type(self) -> Optional[int]:
        """ Type of the Room (always 0 for TextRoom)"""
        return getattr(self, '_type', None)

    @property
    def emoji(self) -> Optional[str]:
        """ The assigned emoji of the room """
        return getattr(self, '_emoji', None)

    @property
    def description(self) -> Optional[str]:
        """ The description of the Room """
        return getattr(self, '_description', None)

    async def send(self, content: str, delay: float = None) -> Optional[Message]:
        """
        Sends a message in the current room.
        
        :param content: Content of the message
        :param delay: Seconds to wait until sending the message (in seconds)
        :return: A new message object if the request was successful
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)
            resp = await self._client.http.post(
                f"/rooms/{self.id}/messages",
                json={"content": content}
            )
            raw_data = await resp.json()

            # Raw_data not in correct format => needs to access data field
            data = raw_data.get('data')
            data = Message.format_obj_data(data)
            return Message(data, self._client)

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to send message in room {repr(self)}",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return None

    async def edit(self, **kwargs) -> bool:
        """
        Changes the rooms data on Hiven

        Available options: emoji, name, description

        :return: True if the request was successful else False
        """
        try:
            for key in kwargs.keys():
                if key in ['emoji', 'name', 'description']:
                    await self._client.http.patch(
                        f"/rooms/{self.id}", json={key: kwargs.get(key)}
                    )

                    return True
                else:
                    raise NameError(
                        "The passed value does not exist in the Room!"
                    )

        except Exception as e:
            keys = "".join(
                key + " " for key in kwargs.keys()
            ) if kwargs != {} else ''
            utils.log_traceback(
                brief=f"Failed to change the values {keys} in room {repr(self)}",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return False

    async def start_typing(self) -> bool:
        """
        Adds the client to the list of users typing
            
        :return: True if the request was successful else False
        """
        try:
            await self._client.http.post(f"/rooms/{self.id}/typing")

            return True

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to create invite for house {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return False

    async def get_recent_messages(self) -> Optional[List[Message]]:
        """
        Gets the recent messages from the current room
            
        :return: A list of all messages in form of Message instances if
        successful.
        """
        try:
            raw_data = await self._client.http.get(f"/rooms/{self.id}/messages")
            raw_data = await raw_data.json()

            data = raw_data.get('data')

            messages_ = []
            for _ in data:
                msg = Message(_, self._client)
                messages_.append(msg)

            return messages_

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to create invite for house {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception
            return None
