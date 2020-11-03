import sys

class User():
    """openhivenpy.Types.User: Data Class for a Hiven User
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with events, guilds user lists, client user attribute and get_user()
    
    """
    def __init__(self, data):
        try:
            self._username = data['user']['username']
            self._name = data['user']['name']
            self._id = data['user']['id']
            self._flags = data["user"]["user_flags"] #ToDo: Discord.py-esque way of user flagss
            if hasattr(data['user'], 'bot'): self._icon = data['user']['icon'] if data['user']['icon'] != None else None
            else: self._icon = None
            if hasattr(data['user'], 'header'): self._header = data['user']['header'] if data['user']['header'] != None else None
            else: self._header = None
            if hasattr(data['user'], 'bot'): self._bot = data['user']['bot'] if data['user']['bot'] != None else False
            else: self._bot = None
            if hasattr(data['user'], 'location'): self._location = data['user']['location'] if data['user']['location'] != None else None
            else: self._location = None
            if hasattr(data['user'], 'website'): self._website = data['user']['website'] if data['user']['website'] != None else None    
            else: self._website = None
            if hasattr(data['user'], 'user'): self._presence = data['user']['presence'] if data['user']['presence'] != None else None #ToDo: Presence class
            else: self._presence = None
            
        except AttributeError: 
            raise AttributeError("The data of the object User was not initialized correctly")
        
        except Exception as e: 
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
        return self._icon

    @property
    def header(self) -> dict:
        return self._header
    
    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def location(self) -> str:
        return self._location

    @property
    def website(self) -> str:
        return self._website