import logging
import sys
import asyncio
import typing
from marshmallow import Schema, fields, post_load, ValidationError, INCLUDE, EXCLUDE

from . import HivenObject
from . import message
from . import user as module_user  # Import as 'module_user' so it does not interfere with property @user
from .. import utils
from .. import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['PrivateGroupRoom', 'PrivateRoom']


class PrivateGroupRoomSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    id = fields.Int(required=True)
    last_message_id = fields.Int(required=True, allow_none=True)
    recipients = fields.List(fields.Field(), required=True)
    name = fields.Str(required=True)
    type = fields.Int(required=True)
    emoji = fields.Raw(allow_none=True)
    description = fields.Str(allow_none=True)
    client_user = fields.Raw(required=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new PrivateGroupRoom Object
        """
        return PrivateGroupRoom(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_GROUP_SCHEMA = PrivateGroupRoomSchema()


class PrivateRoomSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    id = fields.Int(required=True)
    last_message_id = fields.Int(required=True, allow_none=True)
    recipient = fields.Raw(required=True)
    name = fields.Str(required=True)
    type = fields.Int(required=True)
    emoji = fields.Raw(allow_none=True)
    description = fields.Str(allow_none=True)
    client_user = fields.Raw(required=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new PrivateGroupRoom Object
        """
        return PrivateRoom(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = PrivateRoomSchema()


class PrivateGroupRoom(HivenObject):
    """
    Represents a private group chat room with multiple person
    """
    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._last_message_id = kwargs.get('last_message_id')
        self._recipients = kwargs.get('recipients')
        self._name = kwargs.get('name')
        self._description = kwargs.get('description')
        self._emoji = kwargs.get('emoji')
        self._type = kwargs.get('type')
        self._client_user = kwargs.get('client_user')

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipients),
            ('type', self.type)
        ]
        return '<PrivateGroupRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        http,
                        users: typing.List[module_user.User],
                        client_user: module_user.User):
        """
        Creates an instance of the PrivateGroupRoom Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param users: The cached users list to fetch the user from if it already exists or adding it
        :param client_user: The client user in the private room
        :return: The newly constructed PrivateGroupRoom Instance
        """
        try:
            data['id'] = utils.convert_value(int, data.get('id'))
            data['owner_id'] = utils.convert_value(int, data.get('owner_id'))
            data['last_message_id'] = utils.convert_value(int, data.get('last_message_id'))

            _recipients = []
            for d in data.get("recipients"):
                cached_user = utils.get(users, id=utils.convert_value(int, d.get('id')))
                # Testing if the user was already created or if the object needs to be entirely newly created
                if cached_user is None:
                    user_ = await module_user.User.from_dict(d, http)
                    users.append(user_)
                else:
                    user_ = cached_user
                # Adding the user
                _recipients.append(user_)

            data['recipients'] = _recipients
            data['name'] = f"Private Group chat with {(', '.join(getattr(r, 'name') for r in _recipients))}"
            data['client_user'] = client_user

            instance = GLOBAL_GROUP_SCHEMA.load(data, unknown=INCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise errs.InvalidPassedDataError(f"Failed to perform validation in '{cls.__name__}'", data=data) from e

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise errs.InitializationError(f"Failed to initialise {cls.__name__} due to exception:\n"
                                           f"{sys.exc_info()[0].__name__}: {e}!") from e
        else:
            # Adding the http attribute for API interaction
            instance._http = http

            return instance

    @property
    def client_user(self) -> module_user.User:
        return self._client_user

    @property
    def recipients(self) -> typing.List[module_user.User]:
        return self._recipients
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def last_message_id(self) -> int:
        return self._last_message_id    
        
    @property
    def name(self) -> str:
        return self._name 

    @property
    def description(self) -> int:
        return self._description

    @property
    def emoji(self) -> str:
        return self._emoji

    @property
    def type(self) -> int:
        return self._type 

    async def send(self, content: str, delay: float = None) -> typing.Union[message.Message, None]:
        """
        Sends a message in the private room. 

        :param content: Content of the message
        :param delay: Seconds to wait until sending the message (in seconds)
        :return: A Message instance if successful else None
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(
                endpoint=f"/rooms/{self.id}/messages",
                json={"content": content})

            raw_data = await resp.json()
            if raw_data:
                # Raw_data not in correct format => needs to access data field
                data = raw_data.get('data')
                if data:
                    return await message.Message.from_dict(
                        data=data,
                        http=self._http,
                        room_=self,
                        author=self.client_user)
            else:
                raise errs.HTTPResponseError()
        
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_GROUP_ROOM] Traceback:",
                                suffix=f"Failed to send message in room {repr(self)}: \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateGroupRoom.start_call()

        Starts a call with the user in the private room

        :param delay: Delay until calling (in seconds)
        :return: True if successful
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data'):
                # TODO! Needs implementation
                return True
            else:
                raise errs.HTTPResponseError()
            
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_GROUP_ROOM] Traceback:",
                                suffix=f"Failed to start call in {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False         


class PrivateRoom(HivenObject):
    """
    Represents a private chat room with a user
    """
    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._last_message_id = kwargs.get('last_message_id')
        self._recipient = kwargs.get('recipient')
        self._name = kwargs.get('name')
        self._description = kwargs.get('description')
        self._emoji = kwargs.get('emoji')
        self._type = kwargs.get('type')
        self._client_user = kwargs.get('client_user')

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipient),
            ('type', self.type)
        ]
        return '<PrivateRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    @classmethod
    async def from_dict(cls, data: dict, http, client_user, **kwargs):
        """
        Creates an instance of the PrivateRoom Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param client_user: The client user in the private room
        :param kwargs: Additional parameter or instances required for the initialisation
        :return: The newly constructed PrivateRoom Instance
        """
        try:
            data['id'] = utils.convert_value(int, data.get('id'))
            data['last_message_id'] = utils.convert_value(int, data.get('last_message_id'))
            data['recipient'] = await module_user.User.from_dict(data.get('recipients', [])[0], http)
            data['name'] = f"Private chat with {data.get('recipient').name}"
            data['type'] = data.get('type')
            data['client_user'] = client_user

            instance = GLOBAL_SCHEMA.load(data, unknown=EXCLUDE)

        except ValidationError as e:
            utils.log_validation_traceback(cls, e)
            raise errs.InvalidPassedDataError(f"Failed to perform validation in '{cls.__name__}'", data=data) from e

        except Exception as e:
            utils.log_traceback(msg=f"Traceback in '{cls.__name__}' Validation:",
                                suffix=f"Failed to initialise {cls.__name__} due to exception:\n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise errs.InitializationError(f"Failed to initialise {cls.__name__} due to exception:\n"
                                           f"{sys.exc_info()[0].__name__}: {e}!") from e
        else:
            # Adding the http attribute for API interaction
            instance._http = http

            return instance

    @property
    def client_user(self) -> module_user.User:
        return self._client_user

    @property
    def recipient(self) -> module_user.User:
        return self._recipient
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def description(self) -> int:
        return self._description

    @property
    def emoji(self) -> str:
        return self._emoji

    @property
    def last_message_id(self) -> int:
        return self._last_message_id    
        
    @property
    def name(self) -> str:
        return self._name 

    @property
    def type(self) -> int:
        return self._type 
    
    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateRoom.start_call()

        Starts a call with the user in the private room
    
        :param delay: Delay until calling (in seconds)
        :return: True if successful
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None

            resp = await self._http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data'):
                return True
            else:
                return False
            
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_ROOM] Traceback:",
                                suffix=f"Failed to start call in room {repr(self)}: \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False             

    async def send(self, content: str, delay: float = None) -> typing.Union[message.Message, None]:
        """
        Sends a message in the private room. 

        :param content: Content of the message
        :param delay: Delay until sending the message (in seconds)
        :return: Returns a Message Instance if successful.
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(
                endpoint=f"/rooms/{self.id}/messages",
                json={"content": content})

            raw_data = await resp.json()
            if raw_data:
                # Raw_data not in correct format => needs to access data field
                data = raw_data.get('data')
                if data:
                    # Getting the author / self
                    raw_data = await self._http.request(f"/users/@me")
                    author_data = raw_data.get('data')
                    if author_data:
                        msg = await message.Message.from_dict(
                            data=data,
                            http=self._http,
                            room_=self,
                            author=self.client_user)
                        return msg
                    else:
                        raise errs.HTTPReceivedNoDataError()
                else:
                    raise errs.HTTPResponseError()
            else:
                raise errs.HTTPResponseError()
        
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_ROOM] Traceback:",
                                suffix=f"Failed to send message in room {repr(self)}: \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None
