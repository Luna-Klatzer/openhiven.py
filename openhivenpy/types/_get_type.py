from datetime import datetime
from typing import Union

from openhivenpy.gateway.http import HTTP

__all__ = ['getType']


class getType:
    """`openhivenpy.types.getType`
    
    getType Object Returner
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Stores functions that can be called to get Hiven Objects(module types objects)
    
    Only used in the types module to avoid import errors
    
    """
    @staticmethod
    async def a_embed(data: dict):
        """
        Async Function for getting a Embed Object with passed data
        """
        from .embed import Embed
        return Embed(data)

    @staticmethod
    async def a_house(data: dict, http: HTTP, client_id: int):
        """
        Async Function for getting a House Object with passed data 
        """
        from .house import House
        return House(data, http, client_id)

    @staticmethod
    async def a_member(data: dict, house, http: HTTP):
        """
        Async Function for getting a Member Object with passed data 
        """
        from .member import Member
        return Member(data, house, http)
    
    @staticmethod
    async def a_message(data: dict, http: HTTP, house, room, author):
        """
        Async Function for getting a Message Object with passed data 
        """
        from .message import Message
        return Message(data, http, house, room, author)
    
    @staticmethod
    async def a_user(data: dict, http: HTTP):
        """
        Async Function for getting a User Object with passed data 
        """
        from .user import User
        return User(data, http)
    
    @staticmethod
    async def a_room(data: dict, http: HTTP, house):
        """
        Async Function for getting a Room Object with passed data 
        """
        from .room import Room
        return Room(data, http, house)
    
    @staticmethod
    async def a_presence(data: dict, user, http: HTTP):
        """
        Async Function for getting a Presence Object with passed data 
        """
        from .presence import Presence
        return Presence(data, user, http)
    
    @staticmethod
    async def a_private_room(data: dict, http: HTTP):
        """
        Async Function for getting a PrivateRoom Object with passed data 
        """
        from .private_room import PrivateRoom
        return PrivateRoom(data, http)
    
    @staticmethod
    async def a_relationship(data: dict, http: HTTP):
        """
        Async Function for getting a Relationship Object with passed data 
        """
        from .relationship import Relationship
        return Relationship(data, http)
    
    @staticmethod
    async def a_mention(data: dict, timestamp: Union[datetime, str], author, http: HTTP):
        """
        Async Function for getting a Mention Object for a user with passed data 
        """        
        from .mention import Mention
        return Mention(data, timestamp, author, http)

    @staticmethod
    async def a_private_group_room(data: dict, http: HTTP):
        """
        Regular Function for getting a PrivateGroupRoom Object for a group chat with passed data 
        """        
        from .private_room import PrivateGroupRoom
        return PrivateGroupRoom(data, http)
    
    # -------------------------------------------
    @staticmethod
    def category(data: dict, http):
        """
        Regular Function for getting a house category
        """
        from .category import Category
        return Category(data, http)

    @staticmethod
    def embed(data: dict):
        """
        Regular Function for getting a Embed Object with passed data
        """
        from .embed import Embed
        return Embed(data)

    @staticmethod
    def house(data: dict, http: HTTP, client_id: int):
        """
        Regular Function for getting a House Object with passed data
        """
        from .house import House
        return House(data, http, client_id)

    @staticmethod
    def member(data: dict, house, http: HTTP):
        """
        Regular Function for getting a Member Object with passed data
        """
        from .member import Member
        return Member(data, house, http)

    @staticmethod
    def message(data: dict, http: HTTP, house, room, author):
        """
        Regular Function for getting a Message Object with passed data
        """
        from .message import Message
        return Message(data, http, house, room, author)

    @staticmethod
    def user(data: dict, http: HTTP):
        """
        Regular Function for getting a User Object with passed data
        """
        from .user import User
        return User(data, http)

    @staticmethod
    def room(data: dict, http: HTTP, house):
        """
        Regular Function for getting a Room Object with passed data
        """
        from .room import Room
        return Room(data, http, house)

    @staticmethod
    def presence(data: dict, user, http: HTTP):
        """
        Regular Function for getting a Presence Object with passed data
        """
        from .presence import Presence
        return Presence(data, user, http)

    @staticmethod
    def private_room(data: dict, http: HTTP):
        """
        Regular Function for getting a PrivateRoom Object with passed data
        """
        from .private_room import PrivateRoom
        return PrivateRoom(data, http)

    @staticmethod
    def relationship(data: dict, http: HTTP):
        """
        Regular Function for getting a Relationship Object with passed data
        """
        from .relationship import Relationship
        return Relationship(data, http)

    @staticmethod
    def mention(data: dict, timestamp: Union[datetime, str], author, http: HTTP):
        """
        Regular Function for getting a Mention Object for a user with passed data
        """
        from .mention import Mention
        return Mention(data, timestamp, author, http)

    @staticmethod
    def private_group_room(data: dict, http: HTTP):
        """
        Regular Function for getting a PrivateGroupRoom Object for a group chat with passed data
        """
        from .private_room import PrivateGroupRoom
        return PrivateGroupRoom(data, http)
