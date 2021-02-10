import logging
import sys
import typing

from marshmallow import Schema, fields, ValidationError, RAISE, post_load

from ..exceptions import exception as errs
from . import HivenObject
from . import user
from .. import utils

logger = logging.getLogger(__name__)

__all__ = ['Relationship']


class RelationshipSchema(Schema):
    user_id = fields.Int(required=True, allow_none=True)
    user = fields.Raw(required=True, allow_none=True)
    type = fields.Int(required=True)
    id = fields.Int(required=True, allow_none=True)
    recipient_id = fields.Int(required=True, allow_none=True)
    last_updated_at = fields.Raw(allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Relationship Object
        """
        return Relationship(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = RelationshipSchema()


class Relationship(HivenObject):
    """
    Represents a user-relationship with another user or bot

    ---

    Possible Types:
    
    0 - No Relationship
    
    1 - Outgoing Friend Request
    
    2 - Incoming Friend Request
    
    3 - Friend
    
    4 - Restricted User
    
    5 - Blocked User
    """
    def __init__(self, **kwargs):
        self._user_id = kwargs.get('user_id')
        self._user = kwargs.get('user')
        self._type = kwargs.get('type')
        self._id = kwargs.get('id')
        self._recipient_id = kwargs.get('recipient_id')
        self._last_updated_at = kwargs.get('last_updated_at')

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('recipient_id', self.recipient_id),
            ('user_id', self.user_id),
            ('user', repr(self.user)),
            ('type', self.type)
        ]
        return '<Relationship {}>'.format(' '.join('%s=%s' % t for t in info))

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        http,
                        users: typing.List[user.User]):
        """
        Creates an instance of the Relationship Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param users: The users list to fetch the user from
        :return: The newly constructed Relationship Instance
        """
        try:
            data['user_id'] = utils.convert_value(int, data.get('user_id'))
            if data['user'] is not None:
                data['user'] = await user.User.from_dict(data['user'], http)
                if data['user'] is not None:
                    users.append(data['user'])

            if data['user'] is None:
                data['user'] = utils.get(users, id=utils.convert_value(int, data['user_id']))

            data['type'] = utils.convert_value(int, data.get('type'))
            data['id'] = utils.convert_value(int, data.get('id'))
            data['recipient_id'] = utils.convert_value(int, data.get('recipient_id'))

            instance = GLOBAL_SCHEMA.load(data, unknown=RAISE)
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
    def user(self) -> user.User:
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
