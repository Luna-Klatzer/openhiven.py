import logging
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject

logger = logging.getLogger(__name__)

__all__ = ['Invite']


class Invite(HivenObject):
    """
    Represents an Invite to a Hiven House
    """
    def __init__(self, data: dict, _house, http):
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
        self._house = _house
        self._house_members = data.get('counts', {}).get('house_members')
        self._http = http

    def __str__(self) -> str:
        return repr(self)

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
