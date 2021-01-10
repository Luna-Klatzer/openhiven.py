import asyncio
import logging

from ._get_type import getType
from openhivenpy.gateway.http import HTTP
import openhivenpy.types as types
import openhivenpy.exceptions as errs

logger = logging.getLogger(__name__)

__all__ = ['Invite']


class Invite:
    """`openhivenpy.types.Invite`
    
    Data Class for a Invite
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Represents an Invite to a Hiven House
    
    Attributes
    ~~~~~~~~~~
    
    code: `int` - The invite code itself
    
    url: `int` - Url of the invite to the House
    
    room_id: `int` - ID of the Room where the message was deleted
    
    created_at: `str` - String with the creation date
    
    """
    def __init__(self, data: dict, http: HTTP):
        self._http = http
        
        invite = data.get('invite')
        self._code = invite.get('code')

        if self._code is None:
            logger.warning("[INVITE] Got a non-type invite-code! Data is likely faulty!")

        self._url = "hiven.house/"+self._code
        self._created_at = invite.get('created_at')
        self._house_id = invite.get('house_id')
        self._max_age = invite.get('max_age')
        self._max_uses = invite.get('max_uses')
        self._type = invite.get('type')
        
        house_data = data.get('house')
        _raw_data = asyncio.run(self._http.request(endpoint=f"/users/{house_data.get('owner_id')}"))
        if _raw_data:
            _data = _raw_data.get('data')
            if _data:
                self._house = types.LazyHouse(
                    data=house_data,
                    http=self._http)
            else:
                raise errs.HTTPReceivedNoData()
        else:
            raise errs.HTTPReceivedNoData()

        self._house_members = data.get('counts', {}).get('house_members')

    def __str__(self) -> str:
        return str(repr(self))

    def __repr__(self) -> str:
        info = [
            ('code', self.code),
            ('url', self.url),
            ('created_at', self.created_at),
            ('house_id', self.house_id),
            ('type', self.type),
            ('max_age', self.max_age),
            ('max_uses', self.max_uses),
        ]
        return '<Invite {}>'.format(' '.join('%s=%s' % t for t in info))
    
    @property
    def code(self):
        return self._code
    
    @property
    def url(self):
        return self._url
    
    @property
    def house_id(self):
        return self._house_id
    
    @property
    def max_age(self):
        return self._max_age
    
    @property
    def max_uses(self):
        return self._max_uses
    
    @property
    def type(self):
        return self._type
        
    @property
    def house(self):
        return self._house
    
    @property
    def house_members(self):
        return self._house_members

    @property
    def created_at(self):
        return self._created_at
