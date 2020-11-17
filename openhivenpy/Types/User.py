import sys
import datetime
import logging

import openhivenpy.Exception as errs
from ._get_type import getType
from openhivenpy.Gateway.http import HTTPClient

logger = logging.getLogger(__name__)

class User():
    """`openhivenpy.Types.User` 
    
    Data Class for a Hiven User
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with on_member... events, guilds user lists, client user attribute and get_user()
    
    """
    def __init__(self, data: dict, http_client: HTTPClient):
        try:
            # Messages have the user data nested
            if data.get('user') != None:
                data = data.get('user')

            self._username = data.get('username')
            self._name = data.get('name')
            self._id = data.get('id')
            self._flags = data.get('user_flags') #ToDo: Discord.py-esque way of user flags     
            self._icon = data.get('icon')   
            self._header = data.get('header') 
            self._bot = data.get('bot')
            self._location = data.get('location', "")
            self._website = data.get('website', "") 
            self._presence = data.get('presence', "")#ToDo: Presence class
            self._joined_at = data.get('joined_at', "")
            
            self._http_client = http_client
            
        except AttributeError as e: 
            logger.error(f"Error while initializing a User object: {e}")
            raise errs.FaultyInitialization("The data of the object User was not initialized correctly")
        
        except Exception as e: 
            logger.error(f"Error while initializing a User object: {e}")
            raise sys.exc_info()[0](e)

    @property
    def username(self) -> str:
        return self._username

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def icon(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
    
    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def location(self) -> str:
        return self._location

    @property
    def website(self) -> str:
        return self._website

    # Still needs to be worked out
    @property
    def presence(self):
        return self._presence

    @property
    def joined_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._joined_at[:10]) if self._joined_at != None else None