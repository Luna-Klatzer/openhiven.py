import datetime
import logging
import sys
import typing

from .user import User
from openhivenpy.gateway.http import HTTP
from openhivenpy.utils import raise_value_to_type
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['Member']


class Member(User):
    """`openhivenpy.types.Member` 
    
    Data Class for a Hiven member
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only) and the User Class!
    
    Returned with house house member list and House.get_member()
    
    """
    def __init__(self, data: dict, house, http: HTTP):
        try:
            super().__init__(data.get('user', data), http)
            self._user_id = self._id
            self._house_id = data.get('house_id')
            if self._house_id is None:
                self._house_id = house.id
            self._joined_at = data.get('joined_at')
            self._roles = raise_value_to_type(data.get('roles', []), list)
            
            self._house = house
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"[MEMBER] Failed to initialize the Member object! " 
                         f"> {sys.exc_info()[0].__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Most likely faulty data! " 
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"[MEMBER] Failed to initialize the Member object! " 
                         f"> {sys.exc_info()[0].__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Member object! Possibly faulty data! " 
                                            f"> {sys.exc_info()[0].__name__}, {str(e)}")

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('username', self.username),
            ('name', self.name),
            ('id', self.id),
            ('icon', self.icon),
            ('header', self.header),
            ('bot', self.bot),
            ('house_id', self.house_id),
            ('joined_house_at', self.joined_house_at)
        ]
        return '<Member {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user_id(self) -> int:
        return getattr(self, '_user_id', None)

    @property
    def joined_house_at(self) -> str:
        return getattr(self, '_joined_at', None)

    @property
    def house_id(self) -> int:
        return getattr(self, '_house_id', None)

    @property
    def roles(self) -> list:
        return getattr(self, '_roles', None)

    @property
    def joined_at(self) -> str:
        return getattr(self, '_joined_at', None)

    async def kick(self) -> bool:
        """`openhivenpy.types.Member.kick()`

        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise `HivenException.Forbidden`. 
            
        Returns `True` if successful.
        
        """
        resp = await self._http.delete(f"/{self._house_id}/members/{self._user_id}")
        if not resp.status < 300:
            raise errs.Forbidden()
        else:
            return True
