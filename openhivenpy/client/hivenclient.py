import asyncio
import datetime
import inspect
import sys
import os
import logging
import typing
import inspect
from functools import wraps

from ..settings import load_env
from .. import utils
from .. import types
from ..events import HivenParsers, HivenEventHandler
from ..gateway import Connection, HTTP
from ..exceptions import SessionCreateError, InvalidTokenError, HTTPResponseError, WebSocketFailedError, \
    HivenConnectionError
from .cache import ClientCache

__all__ = ['HivenClient']

logger = logging.getLogger(__name__)

load_env()
USER_TOKEN_LEN = utils.convert_value(int, os.getenv("USER_TOKEN_LEN"))
BOT_TOKEN_LEN = utils.convert_value(int, os.getenv("BOT_TOKEN_LEN"))


class HivenClient(HivenEventHandler):
    """ Main Class for connecting to Hiven and interacting with the API. """
    def __init__(self,
                 *,
                 loop: asyncio.AbstractEventLoop = None,
                 log_ws_output: bool = False,
                 queuing: bool = False):
        """

        :rtype: object
        """
        self._token = ""
        self._connection = Connection(self)
        self._loop = loop
        self._log_ws_output = log_ws_output
        self._queuing = queuing
        self._user = None
        self.storage = ClientCache(log_ws_output)

        # Inheriting the HivenEventHandler class that will call and trigger the parsers for events
        super().__init__(HivenParsers(self))

    def __str__(self) -> str:
        return getattr(self, "name")

    def __repr__(self) -> str:
        info = [
            ('open', self.open),
            ('name', getattr(self.user, 'name', None)),
            ('id', getattr(self.user, 'id', None))
        ]
        return '<HivenClient {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def token(self) -> str:
        return self.storage.get('token', None)

    @property
    def log_ws_output(self) -> str:
        return self.storage.get('log_ws_output', None)

    @property
    def http(self) -> HTTP:
        return getattr(self.connection, 'http', None)

    @property
    def connection(self) -> Connection:
        return getattr(self, '_connection', None)

    @property
    def queuing(self) -> asyncio.AbstractEventLoop:
        return getattr(self, '_queuing', None)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return getattr(self, '_loop', None)

    def run(self,
            token: str,
            *,
            loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
            restart: bool = False) -> None:
        """
        Standard function for establishing a connection to Hiven

        :param token: Token that should be used to connect to Hiven
        :param loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was
                           created yet
        :param restart: If set to True the Client will restart if an error is encountered!
        """
        try:
            # Overwriting the until now None Event Loop
            self._token = token
            self.storage['token'] = token

            if token is None or token == "":
                logger.critical(f"[HIVENCLIENT] Empty Token was passed!")
                raise InvalidTokenError("Empty Token was passed!")

            elif len(token) not in (USER_TOKEN_LEN, BOT_TOKEN_LEN):
                logger.critical(f"[HIVENCLIENT] Invalid Token was passed!")
                raise InvalidTokenError("Invalid Token was passed!")

            self._loop = loop
            self.connection._loop = self._loop
            self.loop.run_until_complete(self.connection.connect(token, restart=restart))

        except KeyboardInterrupt:
            pass

        except (InvalidTokenError, WebSocketFailedError):
            raise

        except SessionCreateError:
            raise

        except Exception as e:
            utils.log_traceback(
                level='critical',
                msg="[HIVENCLIENT] Traceback:",
                suffix=f"Failed to keep alive connection to Hiven: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise HivenConnectionError(
                f"Failed to keep alive connection to Hiven: {sys.exc_info()[0].__name__}: {e}"
            )

    async def close(self):
        """ Closes the Connection to Hiven and stops the running WebSocket and the Event Processing Loop """
        await self.connection.close()
        logger.debug("[HIVENCLIENT] Closing the connection! The WebSocket will stop shortly!")

    @property
    def open(self) -> bool:
        return getattr(self.connection, 'open', False)

    @property
    def connection_status(self) -> int:
        return getattr(self.connection, 'connection_status', None)

    @property
    def startup_time(self) -> int:
        return getattr(self.connection, 'startup_time', None)

    @property
    def message_broker(self):
        return getattr(self.connection.ws, 'message_broker', None)

    @property
    def initialised(self):
        return getattr(self.connection.ws, '_open', False)

    async def edit(self, **kwargs) -> bool:
        """
        Edits the Clients data on Hiven

        ---

        Available options: header, icon, bio, location, website, username

        :return: True if the request was successful else False
        """
        try:
            for key in kwargs.keys():
                if key in ['header', 'icon', 'bio', 'location', 'website', 'username']:
                    resp = await self.http.patch(endpoint="/users/@me", json={key: kwargs.get(key)})

                    if resp.status < 300:
                        return True
                    else:
                        raise HTTPResponseError("Unknown! See HTTP Logs!")
                else:
                    raise NameError("The passed value does not exist in the Client!")

        except Exception as e:
            keys = "".join(str(key + " ") for key in kwargs.keys())

            utils.log_traceback(
                msg="[CLIENT] Traceback:",
                suffix=f"Failed change the values {keys}: \n{sys.exc_info()[0].__name__}: {e}"
            )
            raise

    @property
    def user(self):
        return getattr(self, '_user', None)

    @property
    def username(self) -> str:
        return getattr(self.user, 'username', None)

    @property
    def name(self) -> str:
        return getattr(self.user, 'name', None)

    @property
    def id(self) -> int:
        return getattr(self.user, 'id', None)

    @property
    def icon(self) -> str:
        return getattr(self.user, 'icon', None)

    @property
    def header(self) -> str:
        return getattr(self.user, 'header', None)

    @property
    def bot(self) -> bool:
        return getattr(self.user, 'bot', None)

    @property
    def location(self) -> str:
        return getattr(self.user, 'location', None)

    @property
    def website(self) -> str:
        return getattr(self.user, 'website', None)

    @property
    def presence(self) -> str:
        return getattr(self.user, 'presence', None)

    @property
    def joined_at(self) -> typing.Union[datetime.datetime, None]:
        return getattr(self.user, 'joined_at', None)

    async def get_user(self, user_id: str) -> typing.Union[types.User, None]:
        """
        Fetches a User instance from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param user_id: id of the User
        :return: The User instance if it was found else None
        """
        raw_data = self.find_user(user_id)
        if raw_data:
            return await types.User.create_from_dict(raw_data, self)
        else:
            return None

    def find_user(self, user_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param user_id: id of the User
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['relationship'].get(user_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None

    async def get_house(self, house_id: str) -> typing.Union[types.House, None]:
        """
        Fetches a House from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param house_id: id of the House
        :return: The house instance if it was found else None
        """
        raw_data = self.find_house(house_id)
        if raw_data:
            return await types.House.create_from_dict(raw_data, self)
        else:
            return None

    def find_house(self, house_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param house_id: id of the House
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['houses'].get(house_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None

    async def get_entity(self, user_id: str) -> typing.Union[types.Entity, None]:
        """
        Fetches a Entity instance from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param user_id: id of the Entity
        :return: The Entity instance if it was found else None
        """
        raw_data = self.find_entity(user_id)
        if raw_data:
            return await types.Entity.create_from_dict(raw_data, self)
        else:
            return None

    def find_entity(self, user_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param user_id: id of the User
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['relationship'].get(user_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None

    async def get_room(self, room_id: str) -> typing.Union[types.Room, None]:
        """
        Fetches a Room from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param room_id: id of the Room
        :return: The Room instance if it was found else None
        """
        raw_data = self.find_room(room_id)
        if raw_data:
            return await types.Room.create_from_dict(raw_data, self)
        else:
            return None

    def find_room(self, room_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param room_id: id of the Room
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['rooms']['house'].get(room_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None

    async def get_private_room(self, room_id: str) -> typing.Union[types.PrivateRoom, None]:
        """
        Fetches a single PrivateRoom from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param room_id: id of the PrivateRoom
        :return: The PrivateRoom instance if it was found else None
        """
        raw_data = self.find_private_room(room_id)
        if raw_data:
            return await types.PrivateRoom.create_from_dict(raw_data, self)
        else:
            return None

    def find_private_room(self, room_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param room_id: id of the house
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['rooms']['private']['group'].get(room_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None

    async def get_private_group_room(self, room_id: str) -> typing.Union[types.PrivateGroupRoom, None]:
        """
        Fetches a multi PrivateGroupRoom from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param room_id: id of the PrivateGroupRoom
        :return: The PrivateGroupRoom instance if it was found else None
        """
        raw_data = self.find_private_group_room(room_id)
        if raw_data:
            return await types.PrivateGroupRoom.create_from_dict(raw_data, self)
        else:
            return None

    def find_private_group_room(self, room_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param room_id: id of the PrivateGroupRoom
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['rooms']['private']['group'].get(room_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None

    async def get_relationship(self, user_id: str) -> typing.Union[types.Relationship, None]:
        """
        Fetches a Relationship instance from the cache based on the passed id

        ---

        The returned data of the instance is only a copy from the cache and if changes are made while
        the instance exists the data will not be updated!

        :param user_id: id of the Relationship
        :return: The Relationship instance if it was found else None
        """
        raw_data = self.find_relationship(user_id)
        if raw_data:
            return await types.Relationship.create_from_dict(raw_data, self)
        else:
            return None

    def find_relationship(self, user_id: str) -> typing.Union[dict, None]:
        """
        Fetches a dictionary from the cache based on the passed id

        ---

        The returned dict is only a copy from the cache

        :param user_id: id of the Relationship
        :return: The cached dict if it exists in the cache else None
        """
        raw_data = self.storage['relationship'].get(user_id)
        if raw_data:
            return dict(raw_data)
        else:
            return None
