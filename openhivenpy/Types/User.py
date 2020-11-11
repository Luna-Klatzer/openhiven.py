import sys
import datetime
import logging
import openhivenpy.Exception as errs

logger = logging.getLogger(__name__)

class User():
    """`openhivenpy.Types.User` 
    
    Data Class for a Hiven User
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with on_member... events, guilds user lists, client user attribute and get_user()
    
    """
    def __init__(self, data: dict,token):
        try:
            # Messages have only a reduced version of the classic user/member object
            # So it needs to be checked if the user attribute even exists
            if 'user' in data:
                data = data['user']

            self._TOKEN = token

            if hasattr(data, "username"): self._username = data['username']
            else: self._username = None
                
            if hasattr(data, "name"): self._name = data['name']
            else: self._name = None
            
            self._id = data['id']
            
            if hasattr(data, "user_flags"): self._flags = data['user_flags'] #ToDo: Discord.py-esque way of user flags
            else: self._flags = None
            
            if hasattr(data, 'bot'): self._icon = data['icon'] 
            else: self._icon = None
            
            if hasattr(data, 'header'): self._header = data['header'] 
            else: self._header = None
            
            if hasattr(data, 'bot'): self._bot = data['bot'] 
            else: self._bot = None
            
            if hasattr(data, 'location'): self._location = data['location']
            else: self._location = None
            
            if hasattr(data, 'website'): self._website = data['website']  
            else: self._website = None
            
            if hasattr(data, 'user'): self._presence = data['presence'] #ToDo: Presence class
            else: self._presence = None
            
            if hasattr(data, 'joined_at'): self._joined_at = data['joined_at']
            else: self._joined_at = None
            
        except AttributeError: 
            logger.error(e)
            raise errs.FaultyInitialization("The data of the object User was not initialized correctly")
        
        except Exception as e: 
            logger.error(e)
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

    @property
    def joined_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._joined_at) if self._joined_at != None else None