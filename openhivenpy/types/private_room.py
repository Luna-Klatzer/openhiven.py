import logging
import sys
import asyncio

from ._get_type import getType
from .user import User
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class PrivateGroupRoom():
    """`openhivenpy.types.PrivateGroupRoom`
    
    Data Class for a Private Group Chat Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Represents a private group chat room with multiple person
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._id = int(data['id']) if data.get('id') != None else None
            self._last_message_id = data.get('last_message_id')
            recipients = data.get("recipients")
            self._recipient = getType.User(recipients[0], http_client)
            self._name = f"Private chat with {recipients[0]['name']}"   
            self._type = data.get('type')
             
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f" Failed to initialize the PrivateRoom object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize PrivateRoom object! Most likely faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f" Failed to initialize the PrivateRoom object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize PrivateRoom object! Possibly faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
    @property
    def user(self) -> User:
        return self._recipient
    
    @property
    def recipient(self) -> User:
        return self._recipient
    
    @property
    def id(self) -> User:
        return self._id

    @property
    def last_message_id(self) -> User:
        return self._last_message_id    
        
    @property
    def name(self) -> User:
        return self._name 

    @property
    def type(self) -> User:
        return self._type 

    async def send(self, content: str, delay: float = None) -> getType.Message: #ToDo: Attatchments. Requires to be binary
        """openhivenpy.types.PrivateRoom.send(content)

        Sends a message in the private room. 
        
        Returns a `Message` object if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `str` - Seconds to wait until sending the message

        """
        #POST /rooms/roomid/messages
        #Media: POST /rooms/roomid/media_messages
        execution_code = "Unknown"
        try:
            resp = await self._http_client.post(f"/rooms/{self.id}/messages", 
                                                    json={"content": content})
            execution_code = resp.status
            await asyncio.sleep(delay=delay) if delay != None else None

            resp = await self._http_client.request(f"/users/@me")
            data = resp.get('data', {}) 
            author = getType.User(data, self._http_client)

            msg = await getType.a_Message(data, 
                                          self._http_client,
                                          house=None,
                                          room=self,
                                          author=author)
            return msg
        
        except Exception as e:
            logger.error(f" Failed to send message to Hiven! [CODE={execution_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None


class PrivateRoom():
    """`openhivenpy.types.PrivateRoom`
    
    Data Class for a Private Chat Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Represents a private chat room with a person
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            self._id = int(data['id']) if data.get('id') != None else None
            self._last_message_id = data.get('last_message_id')
            recipients = data.get("recipients")
            self._recipient = getType.User(recipients[0], http_client)
            self._name = f"Private chat with {recipients[0]['name']}"   
            self._type = data.get('type')
             
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f" Failed to initialize the PrivateRoom object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize PrivateRoom object! Most likely faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f" Failed to initialize the PrivateRoom object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize PrivateRoom object! Possibly faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
    @property
    def user(self) -> User:
        return self._recipient
    
    @property
    def recipient(self) -> User:
        return self._recipient
    
    @property
    def id(self) -> User:
        return self._id

    @property
    def last_message_id(self) -> User:
        return self._last_message_id    
        
    @property
    def name(self) -> User:
        return self._name 

    @property
    def type(self) -> User:
        return self._type 

    async def send(self, content: str, delay: float = None) -> getType.Message: #ToDo: Attatchments. Requires to be binary
        """openhivenpy.types.PrivateRoom.send(content)

        Sends a message in the private room. 
        
        Returns a `Message` object if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `str` - Seconds to wait until sending the message

        """
        #POST /rooms/roomid/messages
        #Media: POST /rooms/roomid/media_messages
        execution_code = "Unknown"
        try:
            resp = await self._http_client.post(f"/rooms/{self.id}/messages", 
                                                    json={"content": content})
            execution_code = resp.status
            await asyncio.sleep(delay=delay) if delay != None else None

            resp = await self._http_client.request(f"/users/@me")
            data = resp.get('data', {}) 
            author = getType.User(data, self._http_client)

            msg = await getType.a_Message(data, 
                                          self._http_client,
                                          house=None,
                                          room=self,
                                          author=author)
            return msg
        
        except Exception as e:
            logger.error(f" Failed to send message to Hiven! [CODE={execution_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None
