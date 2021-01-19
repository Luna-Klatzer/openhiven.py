import asyncio
import sys
import os
import logging
from time import time
from typing import Optional, Union

from openhivenpy.settings import load_env
from openhivenpy.gateway.connection import ExecutionLoop
from openhivenpy.gateway.ws import Websocket
from openhivenpy.gateway import Connection, HTTP
from openhivenpy.events import EventHandler
import openhivenpy.exceptions as errs
import openhivenpy.utils as utils
import openhivenpy.types as types

__all__ = 'HivenClient'

logger = logging.getLogger(__name__)


def _check_dependencies() -> None:
    pkgs = ['asyncio', 'typing', 'aiohttp']
    for pkg in pkgs:
        if pkg not in sys.modules:
            logger.critical(f"[CLIENT] Module {pkg} not found in locally installed modules!")
            raise ImportError(f"Module {pkg} not found in locally installed modules!", name=pkg)


class HivenClient(EventHandler):
    """`openhivenpy.client.HivenClient` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Main Class for connecting to Hiven and interacting with the API.
    
    Inherits from EventHandler and API
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven.
                    Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    restart: `bool` - If set to `True` the process will restart if an error occurred while running the websocket.
                    If the restart failed again the program will stop. Defaults to `False`
    
    client_type: `str` - Automatically set if UserClient or BotClient is used.
                        Raises `HivenException.InvalidClientType` if set incorrectly. Defaults to `BotClient`
    
    event_handler: `openhivenpy.events.EventHandler` - Handler for the events. Can be modified and customized if wanted.
                                                        Creates a new one on Default
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
   
    log_ws_output: `bool` - Will additionally to normal debug information also log the ws responses
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the handshake
                            didn't complete successfully. Defaults to `40`
    
    event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions.
                                                        Defaults to None!
    
    """
    def __init__(
                self,
                token: str,
                *,
                event_handler: Optional[EventHandler] = None,
                client_type: Optional[str] = None,
                **kwargs):

        # Loading the openhivenpy.env variables
        load_env()
        # Calling super to make the client it's own event_handler
        super().__init__(self)

        if client_type == "user":
            self._CLIENT_TYPE = "user"
            self._bot = False

        elif client_type == "bot":
            self._CLIENT_TYPE = "bot"
            self._bot = True

        elif client_type is None:
            logger.warning("[CLIENT] Client type is None. Defaulting to BotClient.")
            self._CLIENT_TYPE = "bot"
            self._bot = True

        else:
            logger.error(f"[CLIENT] Expected 'user' or 'bot', got '{client_type}'")
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'")

        _user_token_len = int(os.getenv("USER_TOKEN_LEN"))
        _bot_token_len = int(os.getenv("BOT_TOKEN_LEN"))

        if token is None or token == "":
            logger.critical(f"[CLIENT] Empty Token was passed!")
            raise errs.InvalidToken

        elif len(token) != _user_token_len and len(token) != _bot_token_len:  # Bot TOKEN
            logger.critical(f"[CLIENT] Invalid Token was passed!")
            raise errs.InvalidToken

        _check_dependencies()

        self._TOKEN = token  # Token is const!
        self._event_loop = kwargs.get('event_loop')  # Loop defaults to None!

        if event_handler:
            self.event_handler = event_handler
        else:
            # Using the Client as Event Handler => Using inherited functions!
            self.event_handler = self

        # Websocket and client data are being handled over the Connection Class
        self._connection = Connection(event_handler=self.event_handler,
                                      token=token,
                                      **kwargs)

        # Removed nest_async for now!
        # nest_asyncio.apply(loop=self.loop)

    def __str__(self) -> str:
        return str(getattr(self, "name"))

    def __repr__(self) -> str:
        info = [
            ('type', self._CLIENT_TYPE),
            ('open', self.open),
            ('name', getattr(self.user, 'name')),
            ('id', getattr(self.user, 'id'))
        ]
        return '<HivenClient {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def token(self) -> str:
        return getattr(self, '_TOKEN', None)

    @property
    def http(self) -> HTTP:
        return self.connection.http

    @property
    def connection(self) -> Connection:
        return getattr(self, '_connection', None)

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        return getattr(self, '_event_loop', None)

    async def connect(self, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop()) -> None:
        """`openhivenpy.client.HivenClient.connect()`
        
        Async function for establishing a connection to Hiven.

        Will run in the current running event_loop!

        Parameter:
        ----------

        event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions.
                                                            Defaults to running loop!

        """
        try:
            self._event_loop = event_loop
            self._connection._event_loop = self._event_loop
            await self.connection.connect(event_loop)
        except RuntimeError as e:
            logger.error(f"[CLIENT] Failed to establish connect and session > {e}")
            raise errs.HivenConnectionError(f"Failed to start client session and websocket! > {e}")
        finally:
            return

    def run(self, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop()) -> None:
        """`openhivenpy.client.HivenClient.run()`
        
        Standard function for establishing a connection to Hiven

        Parameter:
        ----------

        event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions.
                                                            Defaults to creating a new loop!

        """
        try:
            self._event_loop = event_loop
            self._connection._event_loop = self._event_loop
            self.event_loop.run_until_complete(self.connection.connect(event_loop))
        except RuntimeError as e:
            logger.error(f"[CLIENT] Failed to establish connect and session > {e}")
            raise errs.HivenConnectionError(f"Failed to start session and establish connection to Hiven! > {e}")
        finally:
            return

    async def destroy(self, reason: str = "", *, exec_loop=True) -> bool:
        """`openhivenpy.HivenClient.destroy()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw a RuntimeError if the client was started in a coroutine or if future coroutines
        are going to get executed!

        Parameter
        ~~~~~~~~

        exec_loop: `bool` - If True closes the execution_loop with the other tasks. Defaults to True

        """
        try:
            if self.connection.closed:
                await self.connection.destroy(exec_loop, reason=reason)
                return True
            else:
                logger.error("[CLIENT] An attempt to close the connection to Hiven failed due to no current active "
                             "Connection!")
                return False

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logger.error(f"[CLIENT] << Failed to close client session and websocket to Hiven! > "
                         f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to close client session and websocket to Hiven! > "
                                     f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")

    async def close(self, reason: str = "", *, exec_loop=True) -> bool:
        """`openhivenpy.HivenClient.close()`
        
        Stops the current connection and running tasks.
        
        Returns `True` if successful

        Parameter
        ~~~~~~~~

        exec_loop: `bool` - If True closes the execution_loop with the other tasks. Defaults to True

        """
        try:
            if self.connection.closed:
                await self.connection.close(exec_loop, reason=reason)
                return True
            else:
                logger.error("[CLIENT] << An attempt to close the connection to Hiven failed "
                             "due to no current active Connection!")
                return False

        except KeyboardInterrupt:
            pass

        except Exception as e:
            logger.error(f"[CLIENT] << Failed to close client session and websocket to Hiven! > "
                         f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to close client session and websocket to Hiven! > "
                                     f"{sys.exc_info()[1].__class__.__name__}, {str(e)}")

    @property
    def client_type(self) -> str:
        return getattr(self, '_CLIENT_TYPE', None)

    @property
    def ready(self) -> bool:
        return self.connection.ready

    @property
    def initialized(self) -> bool:
        """`openhivenpy.HivenClient.initialized`

        True if Websocket and HTTP are connected and running

        """
        return self.connection.initialized

    # Meta data
    # -----------
    @property
    def amount_houses(self) -> int:
        return self.connection.amount_houses

    @property
    def houses(self) -> list:
        return self.connection.houses

    @property
    def users(self) -> list:
        return self.connection.users

    @property
    def rooms(self) -> list:
        return self.connection.rooms

    @property
    def private_rooms(self) -> list:
        return self.connection.private_rooms

    @property
    def relationships(self) -> list:
        return self.connection.relationships

    # Client data
    # -----------
    @property
    def name(self) -> str:
        return self.user.name

    @property
    def user(self) -> types.User:
        return self.connection.user

    # General Connection Properties
    @property
    def connection_status(self) -> str:
        """`openhivenpy.HivenClient.get_connection_status`

        Returns a string with the current connection status.
        
        Can be either 'OPENING', 'OPEN', 'CLOSING' or 'CLOSED'

        """
        return self.connection.connection_status

    @property
    def open(self) -> bool:
        """`openhivenpy.HivenClient.websocket`
        
        Returns `True` if the connection is open
        
        Opposite property to closed
        
        """
        return self.connection.open

    @property
    def closed(self) -> bool:
        """`openhivenpy.HivenClient.closed`

        Returns `True` if the ws connection is closed
        
        Opposite property to open
        
        """
        return self.connection.closed

    @property
    def ws(self) -> Websocket:
        """`openhivenpy.HivenClient.websocket`
        
        Returns the ReadOnly Websocket with it's configuration

        """    
        return self.connection.ws

    @property
    def execution_loop(self) -> ExecutionLoop:
        return self.connection.execution_loop

    @property
    def connection_start(self) -> float:
        """`openhivenpy.HivenClient.connection_start`

        Point of connection start in unix dateformat
        
        """
        return self.connection.connection_start

    @property
    def startup_time(self) -> float:
        return self.connection.startup_time

    @property
    def ping(self) -> Union[float, None]:
        """`openhivenpy.client.HivenClient.ping`
        
        Returns the current ping of the HTTP.
        
        """
        if self.http.ready:
            start_t = time()
            raw_data = asyncio.run(self.http.request("/users/@me"))
            data = raw_data.get('data')
            if data:
                return time() - start_t
            else:
                logger.warning("[CLIENT] Failed to ping Hiven!")
                return None
        else:
            return None

    async def edit(self, **kwargs) -> bool:
        """`openhivenpy.HivenClient.edit()`
        
        Change the signed in user's/bot's data. 
        
        Available options: header, icon, bio, location, website.
        
        Alias for HivenClient.connection.edit()
        
        """
        # Connection Object contains inherited Client data => edit() stored there
        return await self.connection.edit(**kwargs)

    async def fetch_room(self, room_id: int) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.getRoom()`
        
        Returns a cached Hiven Room Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_room()
        
        """
        return utils.get(self.rooms, id=room_id)

    async def fetch_house(self, house_id: int) -> Union[types.House, None]:
        """`openhivenpy.HivenClient.getHouse()`
        
        Returns a cached Hiven Room Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_house()
        
        """
        return utils.get(self.houses, id=house_id)

    async def fetch_user(self, user_id: int) -> Union[types.User, None]:
        """`openhivenpy.HivenClient.getUser()`
        
        Returns a cached Hiven User Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_user()
    
        """
        return utils.get(self.users, id=user_id)

    async def get_house(self, house_id: int) -> Union[types.House, None]:
        """`openhivenpy.HivenClient.get_house()`
        
        Returns a Hiven House Object based on the passed id.
        
        Returns the House if it exists else returns None
        
        """
        try:
            cached_house = utils.get(self.houses, id=house_id)
            if cached_house:
                return cached_house

                # TODO! Needs to be done in the future!
            else:
                return None

        except Exception as e:
            logger.error(f"[CLIENT] Failed to get House based with id {house_id}! > {e}")

    async def get_user(self, user_id: int) -> Union[types.User, None]:
        """`openhivenpy.HivenClient.get_user()`
        
        Returns a Hiven User Object based on the passed id.
        
        Returns the House if it exists else returns None
        
        """
        try:
            cached_user = utils.get(self.users, id=user_id)
            if cached_user:
                raw_data = await self.http.request(endpoint=f"/users/{id}")
                if raw_data:
                    data = raw_data.get('data')
                    if data:
                        user = types.User(data, self.http)
                        self.connection._users.remove(cached_user)
                        self.connection._users.append(user)
                        return user
                    else:
                        logger.warning("[CLIENT] Failed to request user data from the Hiven-API!")
                        return cached_user
                else:
                    logger.warning("[CLIENT] Failed to request user data from the Hiven-API!")
                    return cached_user
            else:
                return None

        except Exception as e:
            logger.error(f"[CLIENT] Failed to get User based with id {user_id}! > {e}")

    async def get_room(self, room_id: int) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.get_room()`
        
        Returns a Hiven Room Object based on the passed house id and room id.
        
        Returns the Room if it exists else returns None
        
        """
        try:
            cached_room = utils.get(self.rooms, id=room_id)
            if cached_room:
                house = cached_room.house

                raw_data = await self.http.request(endpoint=f"/rooms/{room_id}")
                # Currently not possible to request room data from Hiven!
                # Therefore only cached rooms can be accessed at the moment!
                if raw_data:
                    data = raw_data.get('data')
                    if data:
                        room = types.Room(data, self.http, house)
                        # Appending the data to the client cache
                        self.connection._rooms.remove(cached_room)
                        self.connection._rooms.append(room)
                        return room
                    else:
                        logger.warning("[CLIENT] Failed to request room data from the Hiven-API!")
                        return cached_room
                else:
                    logger.warning("[CLIENT] Failed to request room data from the Hiven-API!")
                    return cached_room
            else:
                return None

        except Exception as e:
            logger.error(f"[CLIENT] Failed to get Room with id {room_id}! > {e}")

    async def get_private_room(self, room_id: float) -> Union[types.PrivateRoom, None]:
        """`openhivenpy.HivenClient.get_private_room()`
        
        Returns a Hiven `PrivateRoom` or `GroupChatRoom` Object based on the passed house id and room id.
        
        Returns the Room if it exists else returns None
        
        """
        try:
            cached_private_room = utils.get(self.private_rooms, id=room_id)
            if cached_private_room:
                raw_data = await self.http.request(endpoint=f"/rooms/{room_id}")
                # Currently not possible to request room data from Hiven!
                # Therefore only cached rooms can be accessed at the moment!
                if raw_data:
                    data = raw_data.get('data')
                    if data:
                        room = types.PrivateRoom(data, self.http)
                        # Appending the data to the client cache
                        self.connection._private_rooms.remove(cached_private_room)
                        self.connection._private_rooms.append(room)
                        return room
                    else:
                        logger.warning("[CLIENT] Failed to request private_room data from the Hiven-API!")
                        return cached_private_room
                else:
                    logger.warning("[CLIENT] Failed to request private_room data from the Hiven-API!")
                    return cached_private_room
            else:
                return None

        except Exception as e:
            logger.error(f"[CLIENT] Failed to get Private Room with id {room_id}! > {e}")

    async def create_house(self, name: str) -> types.LazyHouse:
        """`openhivenpy.HivenClient.create_house()`
        
        Creates a new house on Hiven if the limit is not yet reached
        
        Returns a low-level form of the House object!

        Note! The returned house does not have all the necessary data and only the basic data!
        To get the regular house use `utils.get(client.houses, id=house_id)`
        
        """
        try:
            resp = await self.http.post(
                endpoint="/houses",
                json={'name': name})

            if resp.status < 300:
                raw_data = await resp.json()
                if raw_data:
                    data = raw_data.get('data')
                    if data:
                        house = types.LazyHouse(data, self.http)
                        return house
                    else:
                        raise errs.HTTPReceivedNoData()
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            logger.error(f"Failed to create House! > {e}")

    async def delete_house(self, house_id: int) -> Union[int, None]:
        """`openhivenpy.HivenClient.delete_house()`
        
        Deletes a house based on passed id on Hiven
        
        Returns the id of the House if successful
        
        Parameter
        ~~~~~~~~~
        
        house_id: `int` - Id of the house
        
        """
        try:
            cached_house = utils.get(self.houses, id=int(house_id))
            if cached_house:
                resp = await self.http.delete(endpoint=f"/houses/{house_id}")

                if resp.status < 300:
                    return self.user.id
                else:
                    raise errs.HTTPFailedRequest()
            else:
                logger.error(f"The house with id {house_id} does not exist in the client cache!")
                return None

        except Exception as e:
            logger.error(f"Failed to delete House! > {e}")

    async def fetch_invite(self, invite_code: str) -> Union[types.Invite, None]:
        """`openhivenpy.HivenClient.get_invite()`
        
        Fetches an invite from Hiven
        
        Returns an `Invite` Object
        
        """
        try:
            raw_data = await self.http.request(endpoint=f"/invites/{invite_code}")

            data = raw_data.get('data')
            if data:
                return types.Invite(data, self.http)
            else:
                raise errs.HTTPReceivedNoData()

        except Exception as e:
            logger.error(f"Failed to fetch the invite with invite_code '{invite_code}'! > {e}")

    async def get_feed(self) -> Union[types.Feed, None]:
        """`openhivenpy.HivenClient.get_feed()`
        
        Get the current users feed
        
        Returns an `Feed` Object
        
        """
        try:
            raw_data = await self.http.request(endpoint=f"/streams/@me/feed")

            if raw_data:
                data = raw_data.get('data')
                if data:
                    return types.Feed(data, self.http)
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPReceivedNoData()

        except Exception as e:
            logger.error(f"Failed to get the users feed! > {e}")

    async def get_mentions(self) -> Union[list, types.Mention]:
        """`openhivenpy.HivenClient.get_mentions()`
        
        Gets all mentions of the client user
        
        Returns a list of `Mention` Objects
        
        """
        try:
            raw_data = await self.http.request(endpoint=f"/streams/@me/mentions")

            data = raw_data.get('data')
            if data:
                mention_list = []
                for msg_data in data:
                    author = types.User(msg_data.get('author'), self.http)

                    room = utils.get(self.rooms, id=int(msg_data.get('room_id')))

                    message = types.Message(
                        msg_data,
                        self.http,
                        room.house,
                        room,
                        author)
                    mention_list.append(message)

                return mention_list
            else:
                raise errs.HTTPReceivedNoData()

        except Exception as e:
            logger.error(f"Failed to get the users mentions! > {e}")

    async def change_room_settings(self, room_id=None, **kwargs) -> Union[types.Room, None]:
        """`openhivenpy.HivenClient.change_room_settings()`
 
        Changed a room settings if permission are sufficient!
        
        Returns the `Room` object if the room exists in the known rooms
 
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request!
        
        room_id: `int` - Id of the room that should be modified

        room: `openhivenpy.types.Room` - Room object that should be modified
        
        Available Options
        ~~~~~~~~~~~~~~~~~
        
        notification_preference: `int` - Notification preference for the room. 0 = 'all'/1 = 'mentions'/2 = 'none'
        
        """
        try:
            if room_id is None:
                room = kwargs.get('room')
                try:
                    room_id = room.id
                except Exception:
                    room_id = None

                if room_id is None:
                    logger.warning("Failed to perform request due to missing room_id or room!")
                    return None
            else:
                json = {}
                for key in kwargs:
                    # Searching through the possible keys and adding them if they are found!
                    if key in ['notification_preference', 'name']:
                        json[key] = kwargs.get(key)

                resp = await self.http.put(
                    endpoint=f"/users/@me/settings/room_overrides/{room_id}",
                    json=json)

                if resp.status < 300:
                    return utils.get(self.rooms, id=int(room_id))
                else:
                    raise errs.HTTPFailedRequest()

        except Exception as e:
            logger.error(f"Failed to edit the room with id {room_id}! > {e}")
            return None

    async def create_private_room(self, user_id: int or float = None, user: types.User = None) -> Union[types.PrivateRoom, None]:
        """`openhivenpy.UserClient.create_private_room()`
 
        Adds a user to a private chat room where you can send messages.
        
        Called when trying to send a message to a user and not room exists yet
        
        Returns the `User` object if the user exists in the known users
 
        Parameter
        ~~~~~~~~~
        
        Only one is required to execute the request! Defaults to user_id if both are provided!
        
        user_id: `int` - Id of the user that should be added to a private room
        
        user: `openhivenpy.types.User` - User object that should be added to a private room
        
        """
        try:
            # Checking if the user was passed and the id can be found
            if user_id is None and user:
                user_id = getattr(user, 'id', None)
                if user_id is None or not isinstance(user, types.User):
                    logger.error("[CLIENT] Invalid parameter for `create_private_room`! Expected user or user_id! > "
                                 f"<user_id={user_id} user={user}>")
                    raise ValueError(f"Expected correct user initialised object! Not {type(user)}")

            # If both are none it will raise an error
            elif user_id is None and user is None:
                raise ValueError("Expected user or user_id that is not None!")

            resp = await self.http.post(endpoint=f"/users/@me/rooms",
                                        json={'recipient': f"{user_id}"})
            if resp.status < 300:
                raw_data = await resp.json()
                data = raw_data.get('data')
                if data:
                    private_room = types.PrivateRoom(data, self.http)
                    self.connection._private_rooms.append(private_room)
                    return private_room
                else:
                    raise errs.HTTPReceivedNoData()
            else:
                raise errs.HTTPFailedRequest()

        except Exception as e:
            logger.error(f"Failed to send a friend request a user with id {user_id}! > {e}")
            return None
