from openhivenpy.Gateway.http import HTTPClient

class getType():
    """`openhivenpy.Types.getType`
    
    getType Object Returner
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Class that stores the methods for getting objects in the Types Module.
    
    Used for Classes in the Types module for getting objects, without needing to import them.
    
    """
    
    @staticmethod
    async def a_House(data: dict, http_client: HTTPClient):
        from .House import House
        return House(data, http_client)

    @staticmethod
    async def a_Member(data: dict, http_client: HTTPClient):
        from .Member import Member
        return Member(data, http_client)    
    
    @staticmethod
    async def a_Message(data: dict, http_client: HTTPClient):
        from .Message import Message
        return Message(data, http_client)
    
    @staticmethod
    async def a_User(data: dict, http_client: HTTPClient):
        from .User import User
        return User(data, http_client)
    
    @staticmethod
    async def a_Room(data: dict, http_client: HTTPClient):
        from .Room import Room
        return Room(data, http_client)
    
    @staticmethod
    async def a_Presence(data: dict, http_client: HTTPClient):
        from .Presence import Presence
        return Presence(data, http_client)
    
    @staticmethod
    def House(data: dict, http_client: HTTPClient):
        from .House import House
        return House(data, http_client)
    
    @staticmethod
    def Member(data: dict, http_client: HTTPClient):
        from .Member import Member
        return Member(data, http_client)    
    
    @staticmethod
    def Message(data: dict, http_client: HTTPClient):
        from .Message import Message
        return Message(data, http_client)
    
    @staticmethod
    def User(data: dict, http_client: HTTPClient):
        from .User import User
        return User(data, http_client)
    
    @staticmethod
    def Room(data: dict, http_client: HTTPClient):
        from .Room import Room
        return Room(data, http_client)
    
    @staticmethod
    def Presence(data: dict, http_client: HTTPClient):
        from .Presence import Presence
        return Presence(data, http_client)
        
        