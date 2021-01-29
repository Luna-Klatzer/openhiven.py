from datetime import datetime
import logging
import sys
import asyncio

from ._get_type import getType
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['DeletedMessage', 'Message']


class DeletedMessage:
    """`openhivenpy.types.DeletedMessage`
    
    Data Class for a removed Hiven message
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Returned with on_message_delete()
    
    Attributes
    ~~~~~~~~~~
    
    house_id: `int` - ID of the House where the message was deleted
    
    message_id: `int` - ID of the message that was deleted
    
    room_id: `int` - ID of the Room where the message was deleted
    
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
    """`openhivenpy.types.Message`
    
    Data Class for a standard Hiven message
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
    Returned with room message list and House.get_message()
 
    Attributes
    ~~~~~~~~~~
    
    id: `int` - ID of the Message
    
    content: `str` - Simple string content of the message
    
    author: `openhivenpy.types.User` - Author Object
    
    author_id: `int` - ID of the Author that created the message
    
    room: `openhivenpy.types.Room` - Room where the message was sent
    
    room_id: `int` - ID of the Room where the message was deleted
    
    house: `openhivenpy.types.House` - House where the message was sent
    
    house_id: `int` - ID of the House where the message was deleted
    
    created_at: `datetime.datetime` - Creation timestamp
    
    edited_at: `datetime.datetime` - If edited returns a string timestamp else None
    
    attachment: `str` - In work
    
    mentions: `openhivenpy.types.Mention` - A list of Mention objects 
    
    exploding: `None` - In work
    
    """
    def __init__(self, data: dict, http: HTTP, house, room, author):
        try:
            self._id = int(data.get('id'))
            self._author = author
            self._attachment = data.get('attachment')
            self._content = data.get('content')
            
            # Converting to seconds because it's in milliseconds
            if data.get('timestamp') is not None:
                self._timestamp = datetime.fromtimestamp(int(data.get('timestamp')) / 1000) 
            else:
                self._timestamp = None
                
            self._edited_at = data.get('edited_at')
            self._mentions = []
            for _data in data.get('mentions', []):
                self._mentions.append(getType.mention(_data, self._timestamp, self._author, http))

            self._type = data.get('type')  # I believe, 0 = normal message, 1 = system.
            self._exploding = data.get('exploding')
            
            self._house_id = data.get('house_id')
            self._house_id = int(data.get('house_id')) if data.get('house_id') is not None else None
            self._house = house
            self._room_id = int(data.get('room_id')) if data.get('room_id') is not None else None
            self._room = room 
            
            self._embed = getType.embed(data.get('embed')) if data.get('embed') is not None else None

            self._http = http
            
        except AttributeError as e: 
            logger.error(f"[MESSAGE] Failed to initialize the Message object! "
                         f"> {sys.exc_info()[0].__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Message object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"[MESSAGE] Failed to initialize the Message object! "
                         f"> {sys.exc_info()[0].__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Message object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")

    def __str__(self) -> str:
        return str(repr(self))

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
        """`openhivenpy.types.Message.ack`

        Marks the message as read. This doesn't need to be done for bot clients. 
        
        Returns `True` if successful.
        
        Parameter
        ~~~~~~~~~
        
        delay: `float` - Delay until marking the message as read (in seconds)
        
        """
        try:
            await asyncio.sleep(delay=delay)
            resp = await self._http.post(endpoint=f"/rooms/{self.room_id}/messages/{self.id}/ack")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse
        
        except Exception as e:
            logger.error(f"[MESSAGE] Failed to mark message as read {repr(self)}" 
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")

    async def delete(self, delay: float) -> bool:
        """`openhivenpy.types.Message.delete()`

        Deletes the message. Raises Forbidden if not allowed. 
        
        Returns a `DeletedMessage` Object if successful
        
        Parameter
        ~~~~~~~~~
        
        delay: `float` - Delay until deleting the message as read (in seconds)
        
        """
        try:
            await asyncio.sleep(delay=delay)
            
            resp = await self._http.delete(endpoint=f"/rooms/{self.room_id}/messages/{self.id}")
            
            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
        
        except Exception as e:
            logger.error(f"[MESSAGE] Failed to delete the message {repr(self)}!" 
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")

    async def edit(self, content: str) -> bool:
        """`openhivenpy.types.House.edit()`

        Edits a message on Hiven
            
        Returns 'True' if successful.

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
            logger.error(f"[MESSAGE] Failed to edit message {repr(self)}!" 
                         f" > {sys.exc_info()[0].__name__}, {str(e)}")
            return False
