import logging
import sys
import asyncio

from ._get_type import getType
from .user import User
from openhivenpy.gateway.http import HTTP
from openhivenpy.utils.utils import get
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['Relationship']


class Relationship:
    """`openhivenpy.types.Relationship`
    
    Data Class for a Hiven Relationship
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Represents a relationship with a person 
    
    Possible Types
    ~~~~~~~~~~~~~~
    
    0 - No Relationship
    
    1 - Outgoing Friend Request
    
    2 - Incoming Friend Request
    
    3 - Friend
    
    4 - Restricted User
    
    5 - Blocked User

    Expected JSON-DATA
    -------------------
    Already friend:
    ---------------
    {'user_id': string,
    'user': {
        'username': str,
        'user_flags': int,
        'name': str,
        'id': str,
        'icon': str,
        'header': str,
        'bot': bool},
    'type': int,
    'last_updated_at': str}

    # TODO! Needs other types added here!

    """
    def __init__(self, data: dict, http: HTTP):
        try:
            user_data = data.get('user')
            # user_id does not always exist
            self._user_id = data.get('user_id')
            if self._user_id:
                self._user_id = int(self._user_id)
            self._user = getType.user(user_data, http)
            self._type = data.get('type')
            # id does not always exist
            self._id = data.get('id')
            if self._id:
                self._id = int(self._id)
            # recipient_id does not always exist
            self._recipient_id = data.get('recipient_id')
            if self._recipient_id:
                self._recipient_id = int(self.recipient_id)
            self._http = http
            
        except AttributeError as e: 
            logger.error(f"[RELATIONSHIP] Failed to initialize the Relationship object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Relationship object! Most likely faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        except Exception as e: 
            logger.error(f"[RELATIONSHIP] Failed to initialize the Relationship object! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Relationship object! Possibly faulty data! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('recipient_id', self.recipient_id),
            ('user_id', self.user_id),
            ('user', repr(self.user)),
            ('type', self.type)
        ]
        return '<Relationship {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user(self) -> User:
        return self._user

    @property
    def type(self) -> int:
        return self._type

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def recipient_id(self) -> int:
        return self._recipient_id

    @property
    def id(self) -> int:
        return self._id
