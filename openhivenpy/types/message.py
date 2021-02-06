import datetime
import logging
import sys
import asyncio
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from . import mention
from . import embed
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['DeletedMessage', 'Message']


class DeletedMessage(HivenObject):
    """
    Represents a Deleted Message
    """
    def __init__(self, data: dict):
        self._message_id = int(data.get('message_id'))
        self._house_id = int(data.get('house_id'))
        self._room_id = int(data.get('room_id'))

    def __str__(self):
        return f"Deleted message in room {self.room_id}"

    @property
    def message_id(self):
        return int(self._message_id)

    @property
    def house_id(self):
        return int(self._house_id)

    @property
    def room_id(self):
        return int(self._room_id)
    

class Message:
    """
    Data Class for a standard Hiven message
    """
    def __init__(self, data: dict, http, house, room, author):
        try:
            self._id = int(data.get('id'))
            self._author = author
            self._attachment = data.get('attachment')
            self._content = data.get('content')
            
            # Converting to seconds because it's in milliseconds
            if data.get('timestamp') is not None:
                self._timestamp = datetime.datetime.fromtimestamp(int(data.get('timestamp')) / 1000)
            else:
                self._timestamp = None
                
            self._edited_at = data.get('edited_at')
            self._mentions = []
            for _data in data.get('mentions', []):
                self._mentions.append(mention.Mention(_data, self._timestamp, self._author, http))

            self._type = data.get('type')  # I believe, 0 = normal message, 1 = system.
            self._exploding = data.get('exploding')
            
            self._house_id = data.get('house_id')
            self._house_id = int(data.get('house_id')) if data.get('house_id') is not None else None
            self._house = house
            self._room_id = int(data.get('room_id')) if data.get('room_id') is not None else None
            self._room = room 
            
            self._embed = embed.Embed.from_dict(data.get('embed'), http) if data.get('embed') is not None else None

            self._http = http
        
        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to initialize the Message object; \n"
                                       f"{sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Message object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

    def __str__(self) -> str:
        return f"<Message: '{self.id}' from '{self.author.name}'>"

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

    @property
    def id(self):
        return int(self._id)

    @property
    def author(self):
        return self._author

    @property
    def created_at(self):
        return self._timestamp

    @property
    def type(self):
        return self._type

    @property
    def exploding(self):
        return self._exploding

    @property
    def edited_at(self):
        return self._edited_at

    @property
    def room(self):
        return self._room

    @property
    def house(self):
        return self._house

    @property
    def attachment(self):
        return self._attachment

    @property
    def content(self):
        return self._content

    @property
    def mentions(self):
        return self._mentions

    @property
    def room_id(self):
        return self._room_id

    @property
    def house_id(self):
        return self._house_id

    @property 
    def embed(self):
        return self._embed

    async def mark_as_read(self, delay: float) -> bool:
        """
        Marks the message as read. This doesn't need to be done for bot clients.
        
        :param delay: Delay until marking the message as read (in seconds)
        :return: True if the request was successful else False
        """
        try:
            await asyncio.sleep(delay=delay)
            resp = await self._http.post(endpoint=f"/rooms/{self.room_id}/messages/{self.id}/ack")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse
        
        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to mark message as read {repr(self)}; \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def delete(self, delay: float) -> bool:
        """
        Deletes the message. Raises Forbidden if not allowed.
        
        :param delay: Delay until deleting the message as read (in seconds)
        :return: A DeletedMessage object if successful
        """
        try:
            await asyncio.sleep(delay=delay)
            
            resp = await self._http.delete(endpoint=f"/rooms/{self.room_id}/messages/{self.id}")
            
            if not resp.status < 300:
                raise errs.Forbidden()
            else:
                return True
        
        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to delete the message {repr(self)}; \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def edit(self, content: str) -> bool:
        """
        Edits a message on Hiven
            
        :return: True if the request was successful else False
        """
        try:
            resp = await self._http.patch(
                endpoint=f"/rooms/{self.room_id}/messages/{self.id}",
                json={'content': content})

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
    
        except Exception as e:
            utils.log_traceback(msg="[MESSAGE] Traceback:",
                                suffix=f"Failed to edit message {repr(self)}; \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False
