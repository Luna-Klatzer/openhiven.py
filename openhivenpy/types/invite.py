import logging
import sys
import types
import typing
import fastjsonschema

from . import HivenObject
from .. import utils
from . import house
from ..exceptions import InitializationError
logger = logging.getLogger(__name__)

__all__ = ['Invite']


class Invite(HivenObject):
    """ Represents an Invite to a Hiven House """
    schema = {
        'type': 'object',
        'properties': {
            'code': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
            },
            'url': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
            },
            'created_at': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'house_id': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'blocked': {
                'anyOf': [
                    {'type': 'boolean'},
                    {'type': 'null'}
                ],
                'default': None
            },
            'mfa_enabled': {
                'anyOf': [
                    {'type': 'boolean'},
                    {'type': 'null'}
                ],
                'default': None
            },
        },
        'additionalProperties': False,
        'required': []
    }
    json_validator: types.FunctionType = fastjsonschema.compile(schema)

    def __init__(self, **kwargs):
        self._code = kwargs.get('code')
        self._url = kwargs.get('url')
        self._created_at = kwargs.get('created_at')
        self._house_id = kwargs.get('house_id')
        self._max_age = kwargs.get('max_age')
        self._max_uses = kwargs.get('max_uses')
        self._type = kwargs.get('type')
        self._house = kwargs.get('house')
        self._house_members = kwargs.get('house_members')

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

    @classmethod
    def form_object(cls, data: dict) -> dict:
        """
        Validates the data and appends data if it is missing that would be required for the creation of an
        instance.

        ---

        Does NOT contain other objects and only their ids!

        :param data: Dict for the data that should be passed
        :return: The modified dictionary
        """
        if data.get('invite') is not None:
            invite = data.get('invite')
        else:
            invite = data
        data['code'] = invite.get('code')
        data['url'] = "https://hiven.house/{}".format(data['code'])
        data['created_at'] = invite.get('created_at')
        data['house_id'] = invite.get('house_id')
        data['max_age'] = invite.get('max_age')
        data['max_uses'] = invite.get('max_uses')
        data['type'] = invite.get('type')
        data['house_members'] = data.get('counts', {}).get('house_members')

        data = cls.validate(data)
        data['house_id'] = int(data['house_id'])
        data['type'] = int(data['type'])
        return data

    @classmethod
    async def from_dict(cls, data: dict, client):
        """
        Creates an instance of the Invite Class with the passed data

        ---

        Does not update the cache and only read from it!
        Only intended to be used to create a instance to interact with Hiven!

        :param data: Dict for the data that should be passed
        :param client: Client used for accessing the cache
        :return: The newly constructed Invite Instance
        """
        try:
            data['house'] = house.House.from_dict(client.storage['houses'][data['house_id']], client)

            instance = cls(**data)

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise InitializationError(
                f"Failed to initialise {cls.__name__} due to exception:\n{sys.exc_info()[0].__name__}: {e}!"
            )
        else:
            instance._client = client
            return instance

    @property
    def code(self) -> int:
        return getattr(self, '_code', None)

    @property
    def url(self) -> str:
        return getattr(self, '_url', None)
    
    @property
    def house_id(self):
        return getattr(self, '_house_id', None)
    
    @property
    def max_age(self):
        return getattr(self, '_max_age', None)

    @property
    def max_uses(self):
        return getattr(self, '_max_uses', None)
    
    @property
    def type(self):
        return getattr(self, '_type', None)
        
    @property
    def house(self):
        return getattr(self, '_house', None)
    
    @property
    def house_members(self):
        return getattr(self, '_house_members', None)

    @property
    def created_at(self):
        return getattr(self, '_created_at', None)
