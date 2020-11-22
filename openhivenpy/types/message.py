import datetime
import requests
import logging
import sys

from ._get_type import getType
import openhivenpy.exceptions as errs
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class Message():
    """`openhivenpy.types.Message`
    
    Data Class for a standard Hiven message
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with room message list and House.get_message()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient, House):
        try:
            self._id = int(data.get('id'))
            self._author = None # Member(data.get('author_id'), http_client)
            self._roomid = int(data.get('room_id'))
            self._room = None #Need to get room list as this returns room_id
            self._attatchment = data.get('attatchment')
            self._content = data.get('content')
            
            # Converting to seconds because it's in miliseconds
            self._timestamp = datetime.datetime.fromtimestamp(int(data.get('timestamp')) / 10000) if data.get('timestamp') != None else None
            self._edited_at = data.get('edited_at')
            self._mentions = [(getType.Member(x) for x in data.get('mentions', []))] #Thats the first time I've ever done that. Be proud of me kudo!
            
            self._type = data.get('type') # I believe, 0 = normal message, 1 = system.
            self._exploding = data.get('exploding') #..I have no idea.
            
            self.House = House
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Error while initializing a Message object: {e}")
            raise errs.FaultyInitialization("The data of the object Message is not in correct Format")
        
        except Exception as e: 
            logger.error(f"Error while initializing a Message object: {e}")
            raise sys.exc_info()[-1](e)

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
    def edited_at(self):
        return self._edited_at

    @property
    def room(self):
        return self._room

    @property
    def attatchment(self):
        return self._attatchment

    @property
    def content(self):
        return self._content

    @property
    def mentions(self):
        return self._mentions

    async def mark_message_as_read(self) -> bool:
        """`openhivenpy.types.Message.ack`

        Marks the message as read. This doesn't need to be done for bot clients. 
        
        Returns `True` if successful.
        
        """
        res = requests.post(f"https://api.hiven.io/v1/rooms/{self._roomid}/messages/{self._id}/ack")
        if not res.status_code == 204:
            return False
        else:
            return True


    async def delete(self) -> bool:
        """`openhivenpy.types.Message.delete()`

        Deletes the message. Raises Forbidden if not allowed. 
        
        Returns True if successful
        
        """
        