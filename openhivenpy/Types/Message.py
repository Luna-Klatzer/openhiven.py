import datetime
import requests
import logging
import sys

import openhivenpy.Exception as errs
from .Room import Room
from .Member import Member

logger = logging.getLogger(__name__)

class Message():
    """`openhivenpy.Types.Message`
    
    Data Class for a standard Hiven message
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with house room message list and House.get_message()
    
    """
    def __init__(self, data: dict, auth_token: str):
        try:
            self._id = data.get('id')
            self._author = None # Member(data.get('author_id'), auth_token)
            self._roomid = data.get('room_id')
            self._room = None #Need to get room list as this returns room_id
            self._attatchment = data.get('attatchment')
            self._content = data.get('content')
            # Converting to seconds because it's in miliseconds
            self._timestamp = datetime.datetime.fromtimestamp(int(data.get('timestamp')) / 10000) if data.get('timestamp') != None else None
            self._edited_at = datetime.datetime.fromtimestamp(data.get('edited_at')) if data.get('edited_at') != None else None
            self._mentions = [(Member(x) for x in data.get('mentions', []))] #Thats the first time I've ever done that. Be proud of me kudo!
            self._type = data.get('type') # I believe, 0 = normal message, 1 = system.
            self._exploding = data.get('exploding') #..I have no idea.
            self._AUTH_TOKEN = auth_token
            
        except AttributeError as e: 
            logger.error(f"Error while initializing a Message object: {e}")
            raise errs.FaultyInitialization("The data of the object Message was not initialized correctly")
        
        except Exception as e: 
            logger.error(f"Error while initializing a Message object: {e}")
            raise sys.exc_info()[0](e)

    @property
    def id(self):
        return self._id

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
        """`openhivenpy.Types.Message.ack`

        Marks the message as read. This doesn't need to be done for bot clients. 
        
        Returns `True` if successful.
        
        """
        res = requests.post(f"https://api.hiven.io/v1/rooms/{self._roomid}/messages/{self._id}/ack")
        if not res.status_code == 204:
            return False
        else:
            return True


    async def delete(self) -> bool:
        """`openhivenpy.Types.Message.delete()`

        Deletes the message. Raises Forbidden if not allowed. 
        
        Returns True if successful
        
        """
        