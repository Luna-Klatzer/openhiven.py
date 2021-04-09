import logging
import sys
import asyncio
import typing
from marshmallow import fields, post_load, ValidationError, EXCLUDE, Schema

from . import HivenObject
from . import message
from .. import utils
from .. import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['Room']


class RoomSchema(Schema):
    # Validations to check for the datatype and that it's passed correctly =>
    # will throw exception 'ValidationError' in case of an faulty data parsing

    id = fields.Int(required=True)
    name = fields.Str(required=True)
    house_id = fields.Int(required=True)
    position = fields.Int(default=0, required=True)
    type = fields.Int(required=True)
    emoji = fields.Raw(default=None, allow_none=True)
    description = fields.Str(default=None, allow_none=True)
    last_message_id = fields.Int(required=True, allow_none=True)
    house = fields.Raw(allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        """
        Returns an instance of the class using the @classmethod inside the Class to initialise the object

        :param data: Dictionary that will be passed to the initialisation
        :param kwargs: Additional Data that can be passed
        :return: A new User Object
        """
        return Room(**data, **kwargs)


# Creating a Global Schema for reuse-purposes
GLOBAL_SCHEMA = RoomSchema()


class Room(HivenObject):
    """
    Represents a Hiven Room inside a House

    ---

    Possible Types:

    0 - Text

    1 - Portal

    """

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._name = kwargs.get('name')
        self._house_id = kwargs.get('house_id')
        self._position = kwargs.get('position')
        self._type = kwargs.get('type')
        self._emoji = kwargs.get('emoji')
        self._description = kwargs.get('description')
        self._last_message_id = kwargs.get('last_message_id')
        self._house = kwargs.get('house')

    def __repr__(self) -> str:
        info = [
            ('name', repr(self.name)),
            ('id', self.id),
            ('house_id', self.house_id),
            ('position', self.position),
            ('type', self.type),
            ('emoji', self.emoji),
            ('description', self.description)
        ]
        return str('<Room {}>'.format(' '.join('%s=%s' % t for t in info)))

    @classmethod
    async def from_dict(cls,
                        data: dict,
                        http,
                        *,
                        houses: typing.Optional[typing.List] = None,
                        house: typing.Optional[typing.Any] = None,
                        **kwargs):
        """
        Creates an instance of the Room Class with the passed data

        :param data: Dict for the data that should be passed
        :param http: HTTP Client for API-interaction and requests
        :param houses: The cached list of Houses to automatically fetch the corresponding House from
        :param house: House passed for the Room. Requires direct specification to work with the Invite
        :return: The newly constructed Room Instance
        """
        try:
            data['id'] = utils.convert_value(int, data.get('id'))
            data['house_id'] = utils.convert_value(int, data.get('house_id'))
            data['last_message_id'] = utils.convert_value(int, data.get('last_message_id'))

            if house is not None:
                data['house'] = house
            elif houses is not None:
                data['house'] = utils.get(houses, id=utils.convert_value(int, data['house']['id']))
            else:
                raise TypeError(f"Expected Houses or single House! Not {type(house)}, {type(houses)}")

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
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def house_id(self) -> int:
        return self._house_id

    @property
    def house(self):
        return self._house

    @property
    def position(self) -> int:
        return self._position

    @property
    def type(self) -> int:
        return self._type  # ToDo: Other room classes.

    @property
    def emoji(self):
        return self._emoji.get("data") if self._emoji is not None else None  # Random type attrib there aswell

    @property
    def description(self) -> typing.Union[str, None]:
        return self._description

    async def send(self, content: str, delay: float = None) -> typing.Union[message.Message, None]:
        """
        Sends a message in the current room.
        
        :param content: Content of the message
        :param delay: Seconds to wait until sending the message (in seconds)
        :return: A new message object if the request was successful
        """
        try:
            await asyncio.sleep(delay=delay) if delay is not None else None
            resp = await self._http.post(f"/rooms/{self.id}/messages", json={"content": content})

            raw_data = await resp.json()
            if raw_data:
                # Raw_data not in correct format => needs to access data field
                data = raw_data.get('data')
                if data:
                    return await message.Message.from_dict(
                        data=data,
                        http=self._http,
                        room_=self,
                        house_=self.house,
                        users=self.house.members)
                else:
                    raise errs.HTTPResponseError()
            else:
                raise errs.HTTPResponseError()

        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to send message in room {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def edit(self, **kwargs) -> bool:
        """
        Changes the rooms data on Hiven

        Available options: emoji, name, description

        :return: True if the request was successful else False
        """
        try:
            for key in kwargs.keys():
                if key in ['emoji', 'name', 'description']:
                    resp = await self._http.patch(f"/rooms/{self.id}", json={key: kwargs.get(key)})

                    if resp.status < 300:
                        return True
                    else:
                        raise errs.HTTPResponseError("Unknown! See HTTP Logs!")
                else:
                    raise NameError("The passed value does not exist in the Room!")

        except Exception as e:
            keys = "".join(key + " " for key in kwargs.keys()) if kwargs != {} else ''

            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to change the values {keys} in room {repr(self)}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def start_typing(self) -> bool:
        """
        Adds the client to the list of users typing
            
        :return: True if the request was successful else False
        """
        try:
            resp = await self._http.post(f"/rooms/{self.id}/typing")

            if resp.status < 300:
                return True
            else:
                raise errs.HTTPResponseError("Unknown! See HTTP Logs!")

        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to create invite for house {self.name} with id {self.id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False

    async def get_recent_messages(self) -> typing.Union[list, message.Message, None]:
        """
        Gets the recent messages from the current room
            
        :return: A list of all messages in form of Message instances if successful.
        """
        try:
            raw_data = await self._http.request(f"/rooms/{self.id}/messages")
            data = raw_data.get('data')

            if data:
                messages_ = []
                for d in data:
                    raw_data = await self._http.request(f"/users/{d.get('author_id')}")
                    if raw_data:
                        author_data = raw_data.get('data')
                        if author_data:
                            author = utils.get(self.house.members,
                                               id=utils.convert_value(int, author_data.get('room_id')))
                            msg = await d.Message.from_dict(
                                data=d,
                                http=self._http,
                                house_=self.house,
                                room_=self,
                                author=author)
                            messages_.append(msg)
                        else:
                            raise errs.HTTPReceivedNoDataError()
                    else:
                        raise errs.HTTPReceivedNoDataError()

                return messages_

            else:
                raise errs.HTTPReceivedNoDataError()

        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to create invite for house {self.name} with id {self.id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None
