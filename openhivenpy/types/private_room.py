import logging
import sys
import asyncio
import typing
from marshmallow import Schema, fields, post_load, ValidationError, RAISE

from . import HivenObject
from . import message
from . import user as module_user  # Import as 'module_user' so it does not interfere with property @user
from .. import utils
from ..exceptions import exception as errs

logger = logging.getLogger(__name__)

__all__ = ['PrivateGroupRoom', 'PrivateRoom']


class PrivateGroupRoom(HivenObject):
    """
    Represents a private group chat room with multiple person
    """
    def __init__(self, data: dict, http):
        try:
            self._id = int(data.get('id'))
            self._last_message_id = data.get('last_message_id')
            
            recipients_data = data.get("recipients")
            self._recipients = []
            for recipient in recipients_data:
                self._recipients.append(module_user.User(recipient, http))
                
            self._name = f"Private Group chat with {(''.join(r.name+', ' for r in self._recipients))[:-2]}"   
            self._type = data.get('type')
             
            self._http = http
        
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_GROUP_ROOM] Traceback:",
                                suffix="Failed to initialize the PrivateRoom object; \n"
                                       f"{sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize PrivateRoom object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipients),
            ('type', self.type)
        ]
        return '<PrivateGroupRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def recipients(self) -> typing.Union[module_user.User, list]:
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
                    # Getting the author / self
                    raw_data = await self._http.request(f"/users/@me")
                    author_data = raw_data.get('data')
                    if author_data:
                        author = module_user.User(author_data, self._http)
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
            utils.log_traceback(msg="[PRIVATE_GROUP_ROOM] Traceback:",
                                suffix=f"Failed to send message in room {repr(self)}; \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateGroupRoom.start_call()

        Starts a call with the user in the private room

        :param delay: Delay until calling (in seconds)
        :return: True if successful
        """
        try:
            await asyncio.sleep(delay=delay)
            resp = await self._http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data') is True:
                return True
            else:
                return False
            
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_GROUP_ROOM] Traceback:",
                                suffix=f"Failed to start call in {repr(self)}; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return False         


class PrivateRoom:
    """
    Represents a private chat room with a user
    """
    def __init__(self, data: dict, http):
        try:
            self._id = int(data.get('id'))
            self._last_message_id = data.get('last_message_id')
            recipients = data.get("recipients")
            self._recipient = module_user.User(recipients[0], http)
            self._name = f"Private chat with {recipients[0]['name']}"   
            self._type = data.get('type')
             
            self._http = http
        
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_ROOM] Traceback:",
                                suffix="Failed to initialize the PrivateRoom object; \n"
                                       f"{sys.exc_info()[0].__name__}: {e} >> Data: {data}")
            raise errs.FaultyInitialization(f"Failed to initialize PrivateRoom object! Possibly faulty data! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('id', self.id),
            ('last_message_id', self.last_message_id),
            ('recipients', self.recipient),
            ('type', self.type)
        ]
        return '<PrivateRoom {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user(self) -> module_user.User:
        return self._recipient
    
    @property
    def recipient(self) -> module_user.User:
        return self._recipient
    
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
    def type(self) -> int:
        return self._type 
    
    async def start_call(self, delay: float = None) -> bool:
        """openhivenpy.types.PrivateRoom.start_call()

        Starts a call with the user in the private room
    
        :param delay: Delay until calling (in seconds)
        :return: True if successful
        """
        try:
            await asyncio.sleep(delay=delay)

            resp = await self._http.post(f"/rooms/{self.id}/call")

            data = await resp.json()
            if data.get('data') is True:
                return True
            else:
                return False
            
        except Exception as e:
            utils.log_traceback(msg="[PRIVATE_ROOM] Traceback:",
                                suffix=f"Failed to start call in room {repr(self)}; \n" 
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
                        author = module_user.User(author_data, self._http)
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
            utils.log_traceback(msg="[PRIVATE_ROOM] Traceback:",
                                suffix=f"Failed to send message in room {repr(self)}; \n" 
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None
