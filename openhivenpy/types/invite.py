import asyncio
import logging

from ._get_type import getType
from openhivenpy.gateway.http import HTTPClient

logger = logging.getLogger(__name__)

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
    def __init__(self, data: dict, http_client: HTTPClient):
        self._http_client = http_client
        
        invite = data.get('invite')
        self._code = invite.get('code')
        self._url = "hiven.house/"+invite.get('code', '')
        self._created_at = invite.get('created_at')
        self._house_id = invite.get('house_id')
        self._max_age = invite.get('max_age')
        self._max_uses = invite.get('max_uses')
        self._type = invite.get('type')
        
        house_data = data.get('house')
        data = asyncio.run(self._http_client.request(f"/users/{house_data.get('owner_id')}"))
        owner = getType.User(data.get('data'), self._http_client)
        self._house = {
            'id': house_data.get('id'),
            'name': house_data.get('name'),
            'owner_id': house_data.get('owner_id'),
            'owner': owner,
            'icon': (f"https://media.hiven.io/v1/houses/"
                    f"{house_data.get('id')}/icons/{house_data.get('icon')}"),
        }
        
        self._house_members = data.get('counts', {}).get('house_members')

    def __str__(self):
        return self._url
    
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
        