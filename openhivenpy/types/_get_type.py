from openhivenpy.gateway.http import HTTPClient
import openhivenpy

class getType():
    """`openhivenpy.types.getType`
    
    getType Object Returner
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Stores functions that can be called to get Hiven Objects(module types objects)
    
    Only used in the types module to avoid import errors
    
    """
    
    @staticmethod
    async def a_House(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a House Object with passed data 
        """
        from .house import House
        return House(data, http_client)

    @staticmethod
    async def a_Member(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Member Object with passed data 
        """
        from .member import Member
        return Member(data, http_client)    
    
    @staticmethod
    async def a_Message(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Message Object with passed data 
        """
        from .message import Message
        return Message(data, http_client)
    
    @staticmethod
    async def a_User(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a User Object with passed data 
        """
        from .user import User
        return User(data, http_client)
    
    @staticmethod
    async def a_Room(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Room Object with passed data 
        """
        from .room import Room
        return Room(data, http_client)
    
    @staticmethod
    async def a_Presence(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Presence Object with passed data 
        """
        from .presence import Presence
        return Presence(data, http_client)
    
    @staticmethod
    async def a_PrivateRoom(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a PrivateRoom Object with passed data 
        """
        from .private_room import PrivateRoom
        return PrivateRoom(data, http_client)
    
    @staticmethod
    async def a_Relationship(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Relationship Object with passed data 
        """
        from .relationship import Relationship
        return Relationship(data, http_client)
    
    
    @staticmethod
    def House(data: dict, http_client: HTTPClient, id: int):
        """
        Regular Function for getting a House Object with passed data 
        """
        from .house import House
        return House(data, http_client, id)
    
    @staticmethod
    def Member(data: dict, http_client: HTTPClient, House):
        """
        Regular Function for getting a Member Object with passed data 
        """
        from .member import Member
        return Member(data, http_client, House)    
    
    @staticmethod
    def Message(data: dict, http_client: HTTPClient, House):
        """
        Regular Function for getting a Message Object with passed data 
        """
        from .message import Message
        return Message(data, http_client, House)
    
    @staticmethod
    def User(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a User Object with passed data 
        """
        from .user import User
        return User(data, http_client)
    
    @staticmethod
    def Room(data: dict, http_client: HTTPClient, House):
        """
        Regular Function for getting a Room Object with passed data 
        """
        from .room import Room
        return Room(data, http_client, House)
    
    @staticmethod
    def Presence(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a Room Object with passed data 
        """
        from .presence import Presence
        return Presence(data, http_client)
        
    @staticmethod
    def PrivateRoom(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a PrivateRoom Object with passed data 
        """
        from .private_room import PrivateRoom
        return PrivateRoom(data, http_client)
    
    @staticmethod
    def Relationship(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a Relationship Object with passed data 
        """
        from .relationship import Relationship
        return Relationship(data, http_client)
        
        