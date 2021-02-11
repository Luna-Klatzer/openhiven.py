import logging
import sys
import typing
from marshmallow import Schema, fields, post_load, ValidationError, INCLUDE

from . import HivenObject
from ..utils import utils

logger = logging.getLogger(__name__)

__all__ = ('Invite', 'InviteSchema')


class InviteSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    type = fields.Int(required=True)
    house = fields.Raw(required=True)
    created_at = fields.Str(default=None, allow_none=True)
    url = fields.Str(required=True)
    house_id = fields.Int(required=True)
    max_age = fields.Raw(required=True, default=None, allow_none=True)
    code = fields.Str(required=True, allow_none=True)
    max_uses = fields.Raw(required=True, allow_none=True)
    house_members = fields.Int(required=True, default=None, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Invite Object
        """
        return Invite(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = InviteSchema()


class Invite(HivenObject):
    """
    Represents an Invite to a Hiven House
    """
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
    async def from_dict(cls,
                        data: dict,
                        http,
                        *,
                        houses: typing.Optional[typing.List] = None,
                        house: typing.Optional[typing.Any] = None,
                        **kwargs):
        """
        Creates an instance of the Invite Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param houses: The cached list of Houses to automatically fetch the corresponding House from
        :param house: House passed for the Invite. Requires direct specification to work with the Invite
        :return: The newly constructed Invite Instance
        """
        try:
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

            if house is not None:
                data['house'] = house
            elif houses is not None:
                data['house'] = utils.get(houses, id=utils.convert_value(int, data['house']['id']))
            else:
                raise TypeError(f"Expected Houses or single House! Not {type(house)}, {type(houses)}")

            instance = GLOBAL_SCHEMA.load(data, unknown=INCLUDE)

            # Adding the http attribute for API interaction
            instance._http = http
            return instance

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            return None

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")

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
