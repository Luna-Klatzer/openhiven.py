import logging
import sys
import asyncio

from ._get_type import getType
from openhivenpy.utils import get
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Room():
    """`openhivenpy.types.Room`
    
    Data Class for a Hiven Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient, house): #These are all the attribs rooms have for now. Will add more when Phin says theyve been updated. Theres no functions. Yet.
        try:
            self._id = int(data.get('id')) if data.get('id') != None else None
            self._name = data.get('name')
            self._house = data.get('house_id')
            self._position = data.get('position')
            self._type = data.get('type') # 0 = Text, 1 = Portal
            self._emoji = data.get('emoji')
            self._description = data.get('description')
            self._last_message_id = data.get('last_message_id')
            
            self._house = house 
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f" Failed to initialize the Room object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize Room object! Most likely faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f" Failed to initialize the Room object! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)} Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initalize Room object! Possibly faulty data! Cause of error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

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
        return self._type #ToDo: Other room classes.

    @property
    def emoji(self):
        return self._emoji.get("data") if self._emoji != None else None #Random type attrib there aswell
    
    @property
    def description(self):
        return self._description

    async def send(self, content: str, delay: float = None) -> getType.Message: #ToDo: Attatchments. Requires to be binary
        """openhivenpy.types.Room.send(content)

        Sends a message in the room. Returns the message if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `str` - Seconds to wait until sending the message

        """
        #POST /rooms/roomid/messages
        #Media: POST /rooms/roomid/media_messages)
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
                                          house=self.house,
                                          room=self,
                                          author=author)
            return msg
        
        except Exception as e:
            logger.error(f" Failed to send message to Hiven! [CODE={execution_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None
        
    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.types.Room.edit()`
        
        Change the rooms data.
        
        Available options: emoji, name, description
        
        Returns `True` if successful
        
        """
        execution_code = "Unknown"
        keys = "".join(key+" " for key in kwargs.keys()) if kwargs != {} else None
        try:
            for key in kwargs.keys():
                if key in ['emoji', 'name', 'description']:
                    resp = await self._http_client.patch(f"/rooms/{self.id}", data={key: kwargs.get(key)})
                    if resp == None:
                        logger.debug(f" Failed to change the values {keys}for room {self.name} with id {self.id}!")
                        return False
                    else:
                        execution_code = resp.status
                        return True
                else:
                    logger.error(" The passed value does not exist in the user context!")
                    raise KeyError("The passed value does not exist in the user context!")
    
        except Exception as e:
            logger.error(f" Failed to change the values {keys}for room {self.name} with id {self.id}. [CODE={execution_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False
        
    async def start_typing(self) -> bool:
        """`openhivenpy.types.House.start_typing()`

        Adds the client to the list of users typing
            
        Returns 'True' if successful.

        """
        execution_code = "Unknown"
        try:
            resp = await self._http_client.post(f"/rooms/{self.id}/typing")
            execution_code = resp.status
            
            return True
    
        except Exception as e:
            logger.error(f" Failed to create invite for house {self.name} with id {self.id}." 
                         f"[CODE={execution_code}] Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return False
        
    async def get_recent_messages(self) -> bool:
        """`openhivenpy.types.House.get_recent_messages()`

        Gets the recent messages from the current room
            
        Returns a list of all messages in form of `message` objects if successful.

        """
        try:
            resp = await self._http_client.request(f"/rooms/{self.id}/messages")
            
            messages = []
            for message in resp.get('data'):
                author_data = await self._http_client.request(f"/users/{message.get('author_id')}")
                if author_data == None:
                    raise errs.HTTPFaultyResponse()
                else:
                    author = await getType.a_User(author_data.get('data'), self._http_client)
                msg = await getType.a_Message(message, self._http_client, self.house, self, author)
                messages.append(msg)
            
            return messages
    
        except Exception as e:
            logger.error(f" Failed to create invite for house {self.name} with id {self.id}." 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            return None 