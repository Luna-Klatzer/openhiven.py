import asyncio
import logging

from ._get_type import getType
from openhivenpy.gateway.http import HTTP

logger = logging.getLogger(__name__)

__all__ = ['Presence']


class Presence:
    """`openhivenpy.types.Presence`
    
    Data Class for a User Presence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    The class inherits all the available data from Hiven(attr -> read-only)!
    
    Represents a User Presence
    
    """
    def __init__(self, data: dict, user, http: HTTP):
        self._http = http
        self._user = user
        self._presence = data.get('presence')

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('presence', self.presence),
            ('user', repr(self.user))
        ]
        return '<Presence {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user(self):
        return self._user

    @property
    def presence(self):
        return self._presence
