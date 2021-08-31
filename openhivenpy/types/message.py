"""
Message File which implements the Hiven Message type and its methods
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

import asyncio
import datetime
import logging
import sys
from typing import Optional, List, Union
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING

from .hiven_type_schemas import MessageSchema, get_compiled_validator, \
    DeletedMessageSchema
from .. import utils
from ..base_types import DataClassObject
from ..exceptions import InvalidPassedDataError, HTTPForbiddenError
from ..utils import log_type_exception

if TYPE_CHECKING:
    from .embed import Embed
    from .textroom import TextRoom
    from .user import User
    from .house import House
    from .mention import Mention
    from .attachment import Attachment
    from .. import HivenClient

logger = logging.getLogger(__name__)

__all__ = ['DeletedMessage', 'Message']


class DeletedMessage(DataClassObject):
    """ Represents a Deleted Message in a Room """
    _json_schema: dict = DeletedMessageSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('DeletedMessage')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._message_id = data.get('message_id')
        self._house_id = data.get('house_id')
        self._room_id = data.get('room_id')
        self._client = client

    def __str__(self):
        return f"Deleted message in room {self.room_id}"

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be
        required for the creation of an
        instance.

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a 
         new class instance
        """
        data = cls.validate(data)
        data['message_id'] = data['id']
        return data

    @property
    def message_id(self) -> Optional[str]:
        """ ID of the original message """
        return getattr(self, '_message_id')

    @property
    def house_id(self) -> Optional[str]:
        """ ID of the original house (None if it does not exist) """
        return getattr(self, '_house_id')

    @property
    def room_id(self) -> Optional[str]:
        """ ID of the original room (can be private) """
        return getattr(self, '_room_id')


class Message(DataClassObject):
    """ Represents a standard Hiven message sent by a user """
    _json_schema: dict = MessageSchema
    json_validator = get_compiled_validator(_json_schema)

    @log_type_exception('Message')
    def __init__(self, data: dict, client: HivenClient):
        super().__init__()
        self._id = data.get('id')
        self._author = data.get('author')
        self._author_id = data.get('author_id')
        self._attachment: Union[dict, Attachment] = data.get('attachment')
        self._content = data.get('content')
        self._timestamp = data.get('timestamp')
        self._edited_at = data.get('edited_at')
        self._mentions = data.get('mentions')
        # I believe, 0 = normal message, 1 = system.
        self._type = data.get('type')
        self._exploding = data.get('exploding')
        self._house_id = data.get('house_id')
        self._house = data.get('house')
        self._room_id = data.get('room_id')
        self._room = data.get('room')
        self._embed = data.get('embed')
        self._bucket = data.get('bucket')
        self._device_id = data.get('device_id')
        self._exploding_age = data.get('exploding_age')
        self._client = client

    def __str__(self) -> str:
        return f"<Message id='{self.id}' from '{self.author.name}'>"

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('content', self.content),
            ('author', repr(self.author)),
            ('room', repr(self.room)),
            ('type', self.type),
            ('exploding', self.exploding),
            ('edited_at', self.edited_at)
        ]
        return '<Message {}>'.format(' '.join('%s=%s' % t for t in info))

    @classmethod
    def format_obj_data(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be
        required for the creation of an
        instance.


        Does NOT contain other objects and only their ids!

        :param data: Data that should be validated and used to form the object
        :return: The modified dictionary, which can then be used to create a 
         new class instance
        """
        # I believe, 0 = normal message, 1 = system.
        data['type'] = utils.safe_convert(int, data.get('type'), None)
        data['bucket'] = utils.safe_convert(int, data.get('bucket'), None)
        data['exploding_age'] = utils.safe_convert(int,
                                                   data.get('exploding_age'),
                                                   None)
        data['timestamp'] = utils.safe_convert(int, data.get('timestamp'))

        data = cls.validate(data)

        if not data.get('room_id') and data.get('room'):
            room_ = data.pop('room')
            if type(room_) is dict:
                room_ = room_.get('id', None)
            elif isinstance(room_, DataClassObject):
                room_ = getattr(room_, 'id', None)
            elif type(data.get('room_id')) is str:
                room_ = data['room_id']
            else:
                room_ = None

            if room_ is None:
                raise InvalidPassedDataError(
                    "The passed room is not in the correct format!", data=data
                )
            else:
                data['room_id'] = room_

        if not data.get('house_id') and data.get('house'):
            house_ = data.pop('house')
            if type(house_) is dict:
                house_ = house_.get('id', None)
            elif isinstance(house_, DataClassObject):
                house_ = getattr(house_, 'id', None)
            elif type(data.get('house_id')) is str:
                house_ = data['house_id']
            else:
                house_ = None

            data['house_id'] = house_

        if not data.get('author_id') and data.get('author'):
            author = data.pop('author')
            if type(author) is dict:
                author = author.get('id', None)
            elif isinstance(author, DataClassObject):
                author = getattr(author, 'id', None)
            elif type(data.get('author_id')) is str:
                author = data['author_id']
            else:
                author = None

            if author is None:
                raise InvalidPassedDataError(
                    "The passed author is not in the correct format!",
                    data=data
                )
            else:
                data['author'] = author

        data['author'] = data['author_id']
        data['house'] = data['house_id']
        data['room'] = data['room_id']
        data['device_id'] = utils.safe_convert(
            str, data.get('device_id'), None
        )
        return data

    @property
    def id(self) -> Optional[str]:
        """ ID of the message """
        return getattr(self, '_id', None)

    @property
    def author_id(self) -> Optional[str]:
        """ ID of the parent Author """
        return getattr(self, '_author_id', None)

    @property
    def author(self) -> Optional[User]:
        """ Returns the Author parent object instance """
        if type(self._author) is str:
            author_id = self._author
        elif type(self.author_id) is str:
            author_id = self.author_id
        else:
            author_id = None

        if type(author_id) is str:
            data = self._client.storage['authors'].get(author_id)
            if data:
                self._author = User(data=data, client=self._client)
                return self._author
            else:
                return None

        elif type(self._author) is User:
            return self._author
        else:
            return None

    @property
    def timestamp(self) -> Optional[datetime.datetime]:
        """ Returns the date the message was created (unix-timestamp) """
        if utils.convertible(int, self._timestamp):
            # Converting to seconds because it's in milliseconds
            self._timestamp = datetime.datetime.fromtimestamp(
                utils.safe_convert(int, self._timestamp) / 1000
            )
            return self._timestamp
        elif type(self._timestamp) is datetime.datetime:
            return self._timestamp
        else:
            return None

    @property
    def type(self) -> Optional[int]:
        """ Returns the type of the message """
        return getattr(self, '_type', None)

    @property
    def exploding(self) -> Optional[bool]:
        """ Returns whether the message is exploding """
        return getattr(self, '_exploding', None)

    @property
    def edited_at(self) -> Optional[str]:
        """ Returns the date the message was edited (unix-timestamp) """
        return getattr(self, '_edited_at', None)

    @property
    def room(self) -> Optional[TextRoom]:
        """ Returns the Room parent object the message was sent in """
        from . import TextRoom
        if type(self._room) is str:
            data = self._client.storage['rooms']['house'].get(self._room)
            if data:
                self._room = TextRoom(data=data, client=self._client)
                return self._room
            else:
                return None

        elif type(self._room) is TextRoom:
            return self._room
        else:
            return None

    @property
    def house(self) -> Optional[House]:
        """
        Returns the House parent object, if the message was sent inside a House
        """
        if type(self._house) is str:
            data = self._client.storage['houses'].get(self._house)
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
    def attachment(self) -> Optional[Attachment]:
        """ Returns the Attachment of the message, if it has one """
        if type(self._attachment) is dict:
            self._attachment: Union[Attachment, dict] = Attachment(
                data=self._attachment, client=self._client
            )
            return self._attachment
        elif type(self._attachment) is Attachment:
            return self._attachment
        else:
            return None

    @property
    def content(self) -> Optional[str]:
        """ Returns the string content of the message """
        return getattr(self, '_content', None)

    @property
    def mentions(self) -> Optional[List[Mention]]:
        """ Returns the mentions of the message """
        from . import Mention
        if type(self._mentions) is list:
            if type(self._mentions[0]) is dict:
                mentions = []
                for d in self._mentions:
                    dict_ = {
                        'timestamp': self.timestamp,
                        'author': self.author,
                        'user': d
                    }
                    mention_data = Mention.format_obj_data(dict_)
                    mentions.append(Mention(mention_data, client=self._client))

                self._mentions = mentions
            return self._mentions
        else:
            return None

    @property
    def room_id(self) -> Optional[str]:
        """ Returns the id of the Room parent object """
        return getattr(self, '_room_id', None)

    @property
    def house_id(self) -> Optional[str]:
        """
        Returns the id of the House parent object,
        if the message was sent inside a House
        """
        return getattr(self, '_house_id', None)

    @property
    def is_house_message(self) -> bool:
        """ Returns whether the message was sent inside a House """
        return self.house_id is not None

    @property
    def embed(self) -> Embed:
        """ Returns the Embed of the message, if it has one """
        return getattr(self, '_embed', None)

    @property
    def bucket(self) -> Optional[int]:
        """ Returns the bucket of the message """
        return getattr(self, '_bucket', None)

    @property
    def device_id(self) -> Optional[str]:
        """ Returns the device id of the author of the message """
        return getattr(self, '_device_id', None)

    @property
    def exploding_age(self) -> Optional[int]:
        """ Returns the exploding age of the message """
        return getattr(self, '_exploding_age', None)

    async def mark_as_read(self, delay: float = None) -> bool:
        """
        Marks the message as read. This doesn't need to be done for bot
        clients.
        
        :param delay: Delay until marking the message as read (in seconds)
        :return: True if the request was successful else False
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)
            await self._client.http.post(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}/ack"
            )
            return True

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to mark message as read {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception

    async def delete(self, delay: float = None) -> bool:
        """
        Deletes the message. Raises Forbidden if not allowed.
        
        :param delay: Delay until deleting the message as read (in seconds)
        :return: A DeletedMessage object if successful
        """
        try:
            if delay is not None:
                await asyncio.sleep(delay=delay)

            resp = await self._client.http.delete(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}"
            )

            if not resp.status < 300:
                raise HTTPForbiddenError()
            else:
                return True

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to delete the message {repr(self)}:",
                exc_info=sys.exc_info()
            )
            # TODO! Raise exception

    async def edit(self, content: str) -> bool:
        """
        Edits a message on Hiven
            
        :return: True if the request was successful else False
        """
        try:
            await self._client.http.patch(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}",
                json={'content': content}
            )
            return True

        except Exception as e:
            utils.log_traceback(
                brief=f"Failed to edit message {repr(self)}",
                exc_info=sys.exc_info()
            )
            return False
