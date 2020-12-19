import logging
import sys
import asyncio
from typing import Union

from ._get_type import getType
from .user import User
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['PrivateGroupRoom', 'PrivateRoom']


class PrivateGroupRoom:
    """`openhivenpy.types.PrivateGroupRoom`
    
    Data Class for a Private Group Chat Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents a private group chat room with multiple person
    
    """
    def __init__(self, data: dict, http: HTTP):
        try:
            self._id = int(data['id']) if data.get('id') is not None else None
            self._last_message_id = data.get('last_message_id')
            
            recipients_data = data.get("recipients")
            self._recipients = []
            for recipient in recipients_data:
                self._recipients.append(getType.user(recipient, http))
                
            self._name = f"Private Group chat with {(''.join(r.name+', ' for r in self._recipients))[:-2]}"   
            self._type = data.get('type')
             
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the PrivateRoom object! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize PrivateRoom object! Most likely faulty data! " 
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the PrivateRoom object! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize PrivateRoom object! Possibly faulty data! "
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self):
        return self.name

    @property
    def recipients(self) -> Union[User, list]:
        return self._recipients
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def last_message_id(self) -> int:
        return self._last_message_id    
        
    @property
    def name(self) -> str:
        return self._name 

    @property
    def type(self) -> int:
        return self._type 

    async def send(self, content: str, delay: float = None) -> getType.message:
        """`openhivenpy.types.PrivateGroupRoom.send()`

        Sends a message in the private room. 
        
        Returns a `Message` object if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `float` - Seconds to wait until sending the message (in seconds)

        """
        # POST /rooms/roomid/messages
        # Media: POST /rooms/roomid/media_messages
        http_code = "Unknown"
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(
                                                f"/rooms/{self.id}/messages",
                                                json={"content": content})
            http_code = resp.status
            data = await resp.json()

            resp = await self._http.request(f"/users/@me")
            author_data = resp.get('data', {})
            author = getType.user(author_data, self._http)

            msg = await getType.a_message(data,
                                          self._http,
                                          house=None,
                                          room=self,
                                          author=author)
            return msg
        
        except Exception as e:
            logger.error(f"Failed to send message to Hiven! [CODE={http_code}] " 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None

    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateGroupRoom.start_call()

        Starts a call with the user in the private room
        
        Returns `True` if successful
        
        Parameter:
        ----------
    
        delay: `float` - Delay until calling (in seconds)

        """
        http_code = "Unknown"
        try:
            await asyncio.sleep(delay=delay)
            resp = await self._http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data') is True:
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(f"Failed to send message to Hiven! [CODE={http_code}] "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False         


class PrivateRoom:
    """`openhivenpy.types.PrivateRoom`
    
    Data Class for a Private Chat Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents a private chat room with a person
    
    """
    def __init__(self, data: dict, http: HTTP):
        try:
            self._id = int(data['id']) if data.get('id') is not None else None
            self._last_message_id = data.get('last_message_id')
            recipients = data.get("recipients")
            self._recipient = getType.user(recipients[0], http)
            self._name = f"Private chat with {recipients[0]['name']}"   
            self._type = data.get('type')
             
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"Failed to initialize the PrivateRoom object! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize PrivateRoom object! Most likely faulty data! "
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"Failed to initialize the PrivateRoom object! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize PrivateRoom object! Possibly faulty data! "
                                            f"Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
    @property
    def user(self) -> User:
        return self._recipient
    
    @property
    def recipient(self) -> User:
        return self._recipient
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def last_message_id(self) -> int:
        return self._last_message_id    
        
    @property
    def name(self) -> str:
        return self._name 

    @property
    def type(self) -> int:
        return self._type 
    
    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateRoom.start_call()

        Starts a call with the user in the private room
        
        Returns `True` if successful
        
        Parameter:
        ----------
    
        delay: `float` - Delay until calling (in seconds)

        """
        http_code = "Unknown"
        try:
            await asyncio.sleep(delay=delay)

            resp = await self._http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data') is True:
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(f"Failed to send message to Hiven! [CODE={http_code}] "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False             

    async def send(self, content: str, delay: float = None) -> Union[getType.message, None]:
        """openhivenpy.types.PrivateRoom.send(content)

        Sends a message in the private room. 
        
        Returns a `Message` object if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `float` - Delay until sending the message (in seconds)

        """
        #POST /rooms/roomid/messages
        #Media: POST /rooms/roomid/media_messages
        http_code = "Unknown"
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(
                                                f"/rooms/{self.id}/messages",
                                                json={"content": content})
            http_code = resp.status

            data = await resp.json()

            resp = await self._http.request(f"/users/@me")
            author_data = resp.get('data', {})
            author = getType.user(author_data, self._http)
            msg = await getType.a_message(data,
                                          self._http,
                                          house=None,
                                          room=self,
                                          author=author)
            return msg
        
        except Exception as e:
            logger.error(f"Failed to send message to Hiven! [CODE={http_code}] "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None
