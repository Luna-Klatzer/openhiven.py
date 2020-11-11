from .Room import Room
from .Member import Member
import requests
class House():
    """`openhivenpy.Types.House`
    
    Data Class for a Hiven House
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the avaible data from Hiven(attr -> read-only)!
    
    Returned with events, the client guilds attribute and get_guild()
    
    """
    def __init__(self, data: dict,token: str):
        self._id = data['id']
        self._name = data['name']
        self._banner = data['banner']
        self._icon = data['icon']
        self._owner_id = data['owner_id']
        self._roles = list(data['entities'])
        self._TOKEN = token
        self._members = list(Member(x,self._TOKEN) for x in data["members"])
        self._rooms = list(Room(x,self._TOKEN) for x in data["rooms"])


    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def banner(self) -> str:
        return self._banner

    @property
    def icon(self) -> str:
        return self._icon
    
    @property
    def owner_id(self) -> int:
        return self._owner_id     
        
    @property
    def roles(self) -> list:
        return self._roles  

    @property
    def users(self) -> list:
        return self._members    
    
    @property
    def members(self) -> list:
        return self._members    
    
    @property
    def rooms(self) -> list:
        return self._rooms    

    @staticmethod
    def create_room(self,name) -> Room:
        """openhivenpy.Types.House.createroom(name)

        Creates a Room in the house with the specified name. Returns the Room that was created if successful
        """
        res = requests.post(f"https://api.hiven.io/v1/houses/{self._id}/rooms",headers={"Content-Type":"application/json","Authorization":self._TOKEN})
        return res #ToDo

    @staticmethod
    def leave(self) -> bool:
        """openhivenpy.Types.House.leave()

        Leaves the House. Returns True if successful."""
        res = requests.delete(f"https://api.hiven.io/v1/houses/{self._id}",headers={"Content-Type":"application/json","Authorization":self._TOKEN})
        return res.status_code == 200