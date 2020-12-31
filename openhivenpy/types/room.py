import logging
import sys
import asyncio
from typing import Union

from ._get_type import getType
from openhivenpy.utils import get
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['Room']


class Room:
    """`openhivenpy.types.Room`
    
    Data Class for a Hiven Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data: dict, http: HTTP, house):
        # These are all the attribs rooms have for now.
        # Will add more when Phin says they've been updated. Theres no functions. Yet.
        try:
            self._id = int(data.get('id')) if data.get('id') is not None else None
            self._name = data.get('name')
            self._house = data.get('house_id')
            self._position = data.get('position')
            self._type = data.get('type')  # 0 = Text, 1 = Portal
            self._emoji = data.get('emoji')
            self._description = data.get('description')
            self._last_message_id = data.get('last_message_id')
            
            self._house = house 
            
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the Room object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Room object! Most likely faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the Room object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Room object! Possibly faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self):
        return self.name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def house(self):
        return self._house

    @property
    def position(self):
        return self._position
    
    @property
    def type(self):
        return self._type  # ToDo: Other room classes.

    @property
    def emoji(self):
        return self._emoji.get("data") if self._emoji is not None else None  # Random type attrib there aswell
    
    @property
    def description(self):
        return self._description

    async def send(self, content: str, delay: float = None) -> getType.message:
        """openhivenpy.types.Room.send()

        Sends a message in the room. Returns the message if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `float` - Seconds to wait until sending the message (in seconds)

        """
        # POST /rooms/roomid/messages
        # Media: POST /rooms/roomid/media_messages
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(
                f"/rooms/{self.id}/messages",
                json={"content": content})
            if resp:
                data = await resp.json()

                raw_data = await self._http.request(f"/users/@me")
                author_data = raw_data.get('data')
                if author_data:
                    author = getType.user(author_data, self._http)
                    msg = await getType.a_message(
                        data=data,
                        http=self._http,
                        house=None,
                        room=self,
                        author=author)
                    return msg
                else:
                    raise errs.HTTPReceivedNoData()

            else:
                raise errs.HTTPFaultyResponse
        
        except Exception as e:
            logger.error(f"Failed to send message to Hiven!  "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None
        
    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.types.Room.edit()`
        
        Change the rooms data.
        
        Available options: emoji, name, description
        
        Returns `True` if successful
        
        """
        try:
            for key in kwargs.keys():
                if key in ['emoji', 'name', 'description']:
                    resp = await self._http.patch(f"/rooms/{self.id}", data={key: kwargs.get(key)})

                    if resp.status < 300:
                        return True
                    else:
                        raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
                else:
                    logger.error("The passed value does not exist in the user context!")
                    raise NameError("The passed value does not exist in the user context!")
    
        except Exception as e:
            keys = "".join(key + " " for key in kwargs.keys()) if kwargs != {} else None
            logger.error(f"Failed to change the values {keys} for room {self.name} with id {self.id}! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False
        
    async def start_typing(self) -> bool:
        """`openhivenpy.types.House.start_typing()`

        Adds the client to the list of users typing
            
        Returns 'True' if successful.

        """
        try:
            resp = await self._http.post(f"/rooms/{self.id}/typing")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
    
        except Exception as e:
            logger.error(f"Failed to create invite for house {self.name} with id {self.id}!" 
                         f" > {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False
        
    async def get_recent_messages(self) -> Union[list, getType.a_message]:
        """`openhivenpy.types.House.get_recent_messages()`

        Gets the recent messages from the current room
            
        Returns a list of all messages in form of `message` objects if successful.

        """
        try:
            raw_data = await self._http.request(f"/rooms/{self.id}/messages")
            data = raw_data.get('data')

            if data:
                messages = []
                for message in data:
                    _raw_data = await self._http.request(f"/users/{message.get('author_id')}")
                    if _raw_data:
                        _author_data = _raw_data.get('data')
                        if _author_data:
                            author = await getType.a_user(_author_data, self._http)
                            msg = await getType.a_message(
                                data=message,
                                http=self._http,
                                house=self.house,
                                room=self,
                                author=author)
                            messages.append(msg)
                        else:
                            raise errs.HTTPReceivedNoData()
                    else:
                        raise errs.HTTPReceivedNoData()

                return messages
            else:
                raise errs.HTTPReceivedNoData()
    
        except Exception as e:
            logger.error(f"Failed to create invite for house {self.name} with id {self.id}!" 
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None
