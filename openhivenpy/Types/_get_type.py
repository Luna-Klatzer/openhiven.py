from openhivenpy.Gateway.http import HTTPClient
import openhivenpy

class getType():
    """`openhivenpy.Types.getType`
    
    getType Object Returner
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Class that stores the methods for getting objects in the Types Module.
    
    Used for Classes in the Types module for getting objects, without needing to import them.
    
    """
    
    @staticmethod
    async def a_House(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a House Object with passed data 
        """
        from .House import House
        return House(data, http_client)

    @staticmethod
    async def a_Member(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Member Object with passed data 
        """
        from .Member import Member
        return Member(data, http_client)    
    
    @staticmethod
    async def a_Message(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Message Object with passed data 
        """
        from .Message import Message
        return Message(data, http_client)
    
    @staticmethod
    async def a_User(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a User Object with passed data 
        """
        from .User import User
        return User(data, http_client)
    
    @staticmethod
    async def a_Room(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Room Object with passed data 
        """
        from .Room import Room
        return Room(data, http_client)
    
    @staticmethod
    async def a_Presence(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Presence Object with passed data 
        """
        from .Presence import Presence
        return Presence(data, http_client)
    
    @staticmethod
    async def a_PrivateRoom(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a PrivateRoom Object with passed data 
        """
        from .PrivateRoom import PrivateRoom
        return PrivateRoom(data, http_client)
    
    @staticmethod
    async def a_Relationship(data: dict, http_client: HTTPClient):
        """
        Async Function for getting a Relationship Object with passed data 
        """
        from .Relationship import Relationship
        return Relationship(data, http_client)
    
    
    @staticmethod
    def House(data: dict, http_client: HTTPClient, id: int):
        """
        Regular Function for getting a House Object with passed data 
        """
        from .House import House
        return House(data, http_client, id)
    
    @staticmethod
    def Member(data: dict, http_client: HTTPClient, House):
        """
        Regular Function for getting a Member Object with passed data 
        """
        from .Member import Member
        return Member(data, http_client, House)    
    
    @staticmethod
    def Message(data: dict, http_client: HTTPClient, House):
        """
        Regular Function for getting a Message Object with passed data 
        """
        from .Message import Message
        return Message(data, http_client, House)
    
    @staticmethod
    def User(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a User Object with passed data 
        """
        from .User import User
        return User(data, http_client)
    
    @staticmethod
    def Room(data: dict, http_client: HTTPClient, House):
        """
        Regular Function for getting a Room Object with passed data 
        """
        from .Room import Room
        return Room(data, http_client, House)
    
    @staticmethod
    def Presence(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a Room Object with passed data 
        """
        from .Presence import Presence
        return Presence(data, http_client)
        
    @staticmethod
    def PrivateRoom(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a PrivateRoom Object with passed data 
        """
        from .PrivateRoom import PrivateRoom
        return PrivateRoom(data, http_client)
    
    @staticmethod
    def Relationship(data: dict, http_client: HTTPClient):
        """
        Regular Function for getting a Relationship Object with passed data 
        """
        from .Relationship import Relationship
        return Relationship(data, http_client)
        
        