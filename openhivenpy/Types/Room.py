import logging
import sys
import asyncio

from ._get_type import getType
import openhivenpy.Exception as errs
from openhivenpy.Gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Room():
    """`openhivenpy.Types.Room`
    
    Data Class for a Hiven Room
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room lists and House.get_room()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient, House): #These are all the attribs rooms have for now. Will add more when Phin says theyve been updated. Theres no functions. Yet.
        try:
            self._id = int(data.get('id')) if data.get('id') != None else None
            self._name = data.get('name')
            self._house = data.get('house_id')
            self._position = data.get('position')
            self._type = data.get('type') # 0 = Text, 1 = Portal
            self._emoji = data.get('emoji')
            self._description = data.get('description')
            self._last_message_id = data.get('last_message_id')
            
            self.House = House 
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Error while initializing a Room object: {e}")
            raise errs.FaultyInitialization("The data of the object Room is not in correct Format")
        
        except Exception as e: 
            logger.error(f"Error while initializing a Room object: {e}")
            raise sys.exc_info()[0](e)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def house(self):
        return None #ToDo

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

    async def send(self, content: str, delay: float) -> getType.Message: #ToDo: Attatchments. Requires to be binary
        """openhivenpy.Types.Room.send(content)

        Sends a message in the room. Returns the message if successful.

        Parameter:
        ----------
        
        content: `str` - Content of the message
    
        delay: `str` - Seconds to wait until sending the message

        """
        #POST /rooms/roomid/messages
        #Media: POST /rooms/roomid/media_messages)
        try:
            response = await self.http_client.post(endpoint="/rooms/{self.id}/messages", 
                                                    data={"content": content})
            await asyncio.sleep(delay=delay)
            msg = await getType.a_Message(response, self.http_client)
            return msg
        
        except Exception as e:
            raise sys.exc_info()[0](e)