import logging
import sys
import typing

from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from . import user
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ('Member', 'MemberSchema')


class MemberSchema(user.UserSchema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing
    user_id = fields.Int(required=True)
    house_id = fields.Int(required=True)
    joined_at = fields.Str(required=True)
    roles = fields.List(fields.Field, required=True, allow_none=True, default=[])
    house = fields.Raw(required=True)
    last_permission_update = fields.Raw(default=None, allow_none=True)
    user = fields.Raw()

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new Member Object
        """
        return Member(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = MemberSchema()


class Member(user.User, HivenObject):
    """
    Represents a House Member on Hiven
    """
    def __init__(self, **kwargs):
        self._user_id = kwargs.get('user_id')
        self._house_id = kwargs.get('house_id')
        self._joined_at = kwargs.get('joined_at')
        self._roles = kwargs.get('roles')
        self._house = kwargs.get('house')
        super().__init__(**kwargs.get('user'))

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

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        http,
                        houses: typing.Optional[typing.List] = None,
                        house: typing.Optional[typing.Any] = None,
                        **kwargs):
        """
        Creates an instance of the Member Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param houses: The cached list of Houses to automatically fetch the corresponding House from
        :param house: House passed for the Member. Requires direct specification to work with the Invite
        :return: The newly constructed Member Instance
        """
        try:
            user_ = data.get('user')
            user_['id'] = utils.convert_value(int, user_.get('id'))
            data['id'] = utils.convert_value(int, user_.get('id'))
            data['user_id'] = data['id']
            data['username'] = user_.get('username')
            data['website'] = user_.get('website', None)
            data['location'] = user_.get('location', None)
            data['name'] = user_.get('name')
            data['roles'] = utils.convert_value(list, data.get('roles'), [])
            if house is not None:
                data['house'] = house
            elif houses is not None:
                data['house'] = utils.get(houses, id=utils.convert_value(int, data['house']['id']))
            else:
                raise TypeError(f"Expected Houses or single House! Not {type(house)}, {type(houses)}")

            # If the house_id exists and works properly it will be directly used
            if utils.convertible(int, data.get('house_id')):
                data['house_id'] = utils.convert_value(int, data.get('house_id'))
            else:
                # else the id of the house object will be used to not pass a None type to the Scheme
                data['house_id'] = data['house'].id

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
    def id(self) -> int:
        return getattr(self, '_user_id', None)

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
        """
        Kicks a user from the house.

        The client needs permissions to kick, or else this will raise `HivenException.Forbidden`
            
        :return: True if the request was successful else HivenException.Forbidden()
        """
        # TODO! Needs be changed with the HTTP Exceptions Update
        resp = await self._http.delete(f"/{self._house_id}/members/{self._user_id}")
        if not resp.status < 300:
            raise errs.Forbidden()
        else:
            return True
