import logging
import sys
import asyncio
import typing
from marshmallow import fields, post_load, ValidationError, RAISE

from . import HivenObject
from . import message
from . import user
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['Room']


class Room(HivenObject):
    """
    Represents a Hiven Room inside a House
    """
    def __init__(self, data: dict, http, house):
        try:
            self._id = utils.convert_value(int, data.get('id'))
            self._name = data.get('name')
            self._house_id = utils.convert_value(int, data.get('house_id'))
            self._position = data.get('position')
            self._type = data.get('type')  # 0 = Text, 1 = Portal
            self._emoji = data.get('emoji')
            self._description = data.get('description')
            self._last_message_id = utils.convert_value(int, data.get('last_message_id'))
            self._house = house

            self._http = http
        
        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to initialize the Room object; \n"
                                       f"> {sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize Room object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

    def __str__(self) -> str:
        return repr(self)

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

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def house_id(self):
        return self._house_id

    @property
    def house(self):
        return self._house

    @property
    def position(self):
        return self._position
    
    @property
    def type(self):
        return self._type  # ToDo: Other room classes.

    @property
    def emoji(self):
        return self._emoji.get("data") if self._emoji is not None else None  # Random type attrib there aswell
    
    @property
    def description(self):
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
                    # Getting the author / self
                    raw_data = await self._http.request(f"/users/@me")
                    author_data = raw_data.get('data')
                    if author_data:
                        author = await user.User.from_dict(author_data, self._http)
                        msg = message.Message(
                            data=data,
                            http=self._http,
                            house=None,
                            room=self,
                            author=author)
                        return msg
                    else:
                        raise errs.HTTPReceivedNoData()
                else:
                    raise errs.HTTPFaultyResponse()
            else:
                raise errs.HTTPFaultyResponse()
        
        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to send message in room {repr(self)}; \n" 
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
                        raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
                else:
                    raise NameError("The passed value does not exist in the user context!")
    
        except Exception as e:
            keys = "".join(key + " " for key in kwargs.keys()) if kwargs != {} else ''

            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to change the values {keys} in room {repr(self)}; \n"
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
                raise errs.HTTPFaultyResponse("Unknown! See HTTP Logs!")
    
        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to create invite for house {self.name} with id {self.id}; \n" 
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
                messages = []
                for message in data:
                    _raw_data = await self._http.request(f"/users/{message.get('author_id')}")
                    if _raw_data:
                        _author_data = _raw_data.get('data')
                        if _author_data:
                            author = await user.User.from_dict(_author_data, self._http)
                            msg = message.Message(
                                data=message,
                                http=self._http,
                                house=self.house,
                                room=self,
                                author=author)
                            messages.append(msg)
                        else:
                            raise errs.HTTPReceivedNoData()
                    else:
                        raise errs.HTTPReceivedNoData()

                return messages
            else:
                raise errs.HTTPReceivedNoData()
    
        except Exception as e:
            utils.log_traceback(msg="[ROOM] Traceback:",
                                suffix=f"Failed to create invite for house {self.name} with id {self.id}; \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None
