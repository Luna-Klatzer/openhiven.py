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

    def __str__(self):
        return self._presence

    @property
    def user(self):
        return self._user

    @property
    def presence(self):
        return self._presence
