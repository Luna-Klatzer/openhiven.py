import asyncio
import sys
import os
import logging
import typing

from ..settings import load_env
from ..gateway.connection import ExecutionLoop
from ..gateway import Connection, HTTP
from ..events import EventHandler
from .. import exception as errs
import openhivenpy.utils as utils
import openhivenpy.types as types

__all__ = 'HivenClient'

logger = logging.getLogger(__name__)

# Loading the environment variables
load_env()
# Setting the default values to the currently set defaults in the openhivenpy.env file
_default_connection_heartbeat = int(os.getenv("CONNECTION_HEARTBEAT"))
_default_close_timeout = int(os.getenv("CLOSE_TIMEOUT"))


def _check_dependencies() -> None:
    packages = ['asyncio', 'typing', 'aiohttp']
    for pkg in packages:
        if pkg not in sys.modules:
            logger.critical(f"[HIVENCLIENT] Module {pkg} not found in locally installed modules!")
            raise ImportError(f"Module {pkg} not found in locally installed modules!", name=pkg)


class HivenClient(EventHandler):
    """
    Main Class for connecting to Hiven and interacting with the API.
    """

    def __init__(
            self,
            token: str,
            *,
            client_type: typing.Optional[str] = "bot",
            heartbeat: typing.Optional[int] = _default_connection_heartbeat,
            event_loop: typing.Optional[asyncio.AbstractEventLoop] = None,
            event_handler: typing.Optional[EventHandler] = None,
            close_timeout: typing.Optional[int] = _default_close_timeout,
            log_ws_output: typing.Optional[bool] = False,
            **kwargs):
        """
        Object Instance Construction

        :param token: Authorisation Token for Hiven
        :param heartbeat: Intervals in which the bot will send heartbeats to the Websocket.
                          Defaults to the pre-set environment heartbeat (30000)
        :param event_handler: Handler for the events. Creates a new one on Default
        :param event_loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no
                           one was created yet
        :param close_timeout: Seconds after the websocket will timeout after the end handshake didn't complete
                              successfully. Defaults to the pre-set environment close_timeout (40)
        :param log_ws_output: Will additionally to normal debug information also log the ws responses
        """

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
            logger.warning("[HIVENCLIENT] Client type is None. Defaulting to BotClient.")
            self._CLIENT_TYPE = "bot"
            self._bot = True

        else:
            logger.error(f"[HIVENCLIENT] Expected 'user' or 'bot', got '{client_type}'")
            raise errs.ClientTypeError(f"Expected 'user' or 'bot', got '{client_type}'")

        _user_token_len = int(os.getenv("USER_TOKEN_LEN"))
        _bot_token_len = int(os.getenv("BOT_TOKEN_LEN"))

        if token is None or token == "":
            logger.critical(f"[HIVENCLIENT] Empty Token was passed!")
            raise errs.InvalidTokenError()

        elif len(token) != _user_token_len and len(token) != _bot_token_len:  # Bot TOKEN
            logger.critical(f"[HIVENCLIENT] Invalid Token was passed!")
            raise errs.InvalidTokenError()

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
                                      heartbeat=heartbeat,
                                      event_loop=event_loop,
                                      close_timeout=close_timeout,
                                      log_ws_output=log_ws_output,
                                      **kwargs)

        # Removed nest_async for now!
        # nest_asyncio.apply(loop=self.loop)

    def __str__(self) -> str:
        return getattr(self, "name")

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
        return getattr(self.connection, '_http', None)

    @property
    def connection(self) -> Connection:
        return getattr(self, '_connection', None)

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        return getattr(self, '_event_loop', None)

    async def connect(self,
                      *,
                      event_loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
                      restart: bool = False) -> None:
        """
        Async function for establishing a connection to Hiven.

        Will run in the current running event_loop and not return unless it's finished!

        :param event_loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was
                           created yet
        :param restart: If set to True the bot will restart if an error is encountered!
        """
        try:
            # Overwriting the event_loop to have the current running event_loop
            self._event_loop = event_loop
            self._connection._event_loop = self._event_loop

            # If the client should restart a task for restart handling will be created
            if restart:
                # Adding the restart handler to the background loop to run infinitely
                # and restart when needed!

                # Note! Restart only works after startup! If the startup fails no restart will be attempted!
                self.connection.execution_loop.add_to_loop(self.connection.handler_restart_websocket())
                self.connection._restart = True

            # Starting the connection to Hiven
            await self.connection.connect(event_loop)

        except KeyboardInterrupt:
            pass

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to establish or keep the connection alive: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise errs.SessionCreateError("Failed to establish HivenClient session!") from e

    def run(self,
            *,
            event_loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
            restart: bool = False) -> None:
        """
        Standard function for establishing a connection to Hiven

        :param event_loop: Event loop that will be used to execute all async functions. Will use
                           'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was
                           created yet
        :param restart: If set to True the bot will restart if an error is encountered!
        """
        try:
            # Overwriting the event_loop to have the current running event_loop
            self._event_loop = event_loop
            self.connection._event_loop = self._event_loop

            # If the client should restart a task for restart handling will be created
            if restart:
                # Adding the restart handler to the background loop to run infinitely
                # and restart when needed!

                # Note! Restart only works after startup! If the startup fails no restart will be attempted!
                self.connection.execution_loop.add_to_loop(self.connection.handler_restart_websocket())
                self.connection._restart = True

            self.event_loop.run_until_complete(self.connection.connect(event_loop))

        except KeyboardInterrupt:
            pass

        except Exception as e:
            utils.log_traceback(level='critical',
                                msg="[HIVENCLIENT] Traceback:",
                                suffix="Failed to establish or keep the connection alive: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}!")
            raise errs.SessionCreateError("Failed to establish HivenClient session!") from e

    async def destroy(self, reason: str = "", *, exec_loop=True) -> bool:
        """
        Kills the event loop and the running tasks!

        Deprecated! Will be removed in later versions

        :param reason: Reason for the destruction that will be logged
        :param exec_loop: If True closes the execution_loop with the other tasks. Defaults to True
        """
        try:
            if self.connection.closed:
                await self.connection.destroy(exec_loop, reason=reason)
                return True
            else:
                logger.error("[HIVENCLIENT] An attempt to close the connection to Hiven failed due to no current active"
                             " Connection!")
                return False

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to close client session and websocket to Hiven: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.ClosingError(f"Failed to close client session and websocket to Hiven! > "
                                    f"{sys.exc_info()[0].__name__}: {e}")

    async def close(self, reason: str = "", *, close_exec_loop=True) -> bool:
        """
        Stops the current connection and running tasks.

        :param reason: Reason for the call of the closing function
        :param close_exec_loop: If True closes the execution_loop with the other tasks. Defaults to True
        :return: True if successful else False
        """
        try:
            if not self.connection.closed:
                await self.connection.close(reason, close_exec_loop)
                return True
            else:
                logger.error("[HIVENCLIENT] An attempt to close the connection to Hiven failed "
                             "due to no current active Connection!")
                return False

        except KeyboardInterrupt:
            pass

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to close client session and websocket to Hiven: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.ClosingError(f"Failed to close client session and websocket to Hiven") from e

    @property
    def client_type(self) -> str:
        return getattr(self, '_CLIENT_TYPE', None)

    @property
    def ready(self) -> bool:
        return getattr(self.connection, 'ready', None)

    @property
    def initialised(self) -> bool:
        """
        True if WebSocket and HTTP-Session are connected and running
        """
        return getattr(self.connection, 'initialised', None)

    @property
    def amount_houses(self) -> int:
        return getattr(self.connection, 'amount_houses', None)

    @property
    def houses(self) -> list:
        return getattr(self.connection, 'houses', None)

    @property
    def users(self) -> list:
        return getattr(self.connection, 'users', None)

    @property
    def rooms(self) -> list:
        return getattr(self.connection, 'rooms', None)

    @property
    def private_rooms(self) -> list:
        return getattr(self.connection, 'private_rooms', None)

    @property
    def relationships(self) -> list:
        return getattr(self.connection, 'relationships', None)

    @property
    def house_memberships(self) -> list:
        return getattr(self.connection, 'house_memberships', None)

    # Client data
    # -----------
    @property
    def name(self) -> str:
        return getattr(self.user, 'name', None)

    @property
    def user(self) -> typing.Union[types.User, None]:
        return getattr(self.connection, '_client_user', None)

    # General Connection Properties
    @property
    def connection_status(self) -> str:
        """
        Returns a string with the current connection status.
        
        Can be either 'OPENING', 'OPEN', 'CLOSING' or 'CLOSED'
        """
        return getattr(self.connection, 'connection_status', None)

    @property
    def open(self) -> bool:
        """
        Returns True if the current connection is open else False
        """
        return getattr(self.connection, 'open', None)

    @property
    def closed(self) -> bool:
        """
        Returns False if the current connection is open else True
        """
        return getattr(self.connection, 'closed', None)

    @property
    def execution_loop(self) -> ExecutionLoop:
        return getattr(self.connection, 'execution_loop', None)

    @property
    def connection_start(self) -> float:
        """
        Point of connection start in unix dateformat
        """
        return getattr(self.connection, 'connection_start', None)

    @property
    def startup_time(self) -> float:
        return getattr(self.connection, 'startup_time', None)

    async def edit(self, **kwargs) -> bool:
        """
        Edits the Clients data on Hiven

        Available options: header, icon, bio, location, website, username

        :param kwargs: The data-fields that will be changed
        :return: True if the request was successful else False
        """
        # Connection Object contains inherited Client data => edit() stored there
        return await self.connection.edit(**kwargs)

    def fetch_room(self, room_id: int) -> typing.Union[types.Room, None]:
        """
        Returns a cached Hiven Room Object

        :param room_id: The id of the room that should be fetched
        :return: The Room Object if it was found
        """
        return utils.get(self.rooms, id=room_id)

    def fetch_house(self, house_id: int) -> typing.Union[types.House, None]:
        """
        Returns a cached Hiven Room Object

        :param house_id: The id of the house that should be fetched
        :return: The User Object if it was found
        """
        return utils.get(self.houses, id=house_id)

    def fetch_user(self, user_id: int) -> typing.Union[types.User, None]:
        """
        Returns a cached Hiven User Object

        :param user_id: The id of the user that should be fetched
        :return: The User Object if it was found
        """
        return utils.get(self.users, id=user_id)

    def fetch_private_room(self, room_id: int) -> typing.Union[types.PrivateRoom, None]:
        """
        Returns a cached Hiven PrivateRoom Object

        :param room_id: The id of the private room that should be fetched
        :return: The PrivateRoom Object if it was found
        """
        return utils.get(self.private_rooms, id=room_id)

    async def get_house(self, house_id: int) -> typing.Union[types.House, None]:
        """
        Returns a Hiven House Object based on the passed ID.

        :param house_id: The id of the house that should be fetched
        :return: The House Object if it was found
        """
        try:
            cached_house = utils.get(self.houses, id=house_id)
            if cached_house:
                return cached_house

                # TODO! Request
            else:
                return None

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to get House based with id {house_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def get_user(self, user_id: int) -> typing.Union[types.User, None]:
        """
        Returns a Hiven User Object based on the passed ID.

        :param user_id: The id of the user that should be fetched
        :return: The User Object if it was found
        """
        # TODO! Needs username added to request options!
        try:
            cached_user = utils.get(self.users, id=user_id)
            if cached_user:

                raw_data = await self.connection.http.request(endpoint=f"/users/{id}")
                if raw_data:
                    data = raw_data.get('data')
                    if data:
                        user = await types.User.from_dict(data, self.connection.http)
                        self.connection._users.remove(cached_user)
                        self.connection._users.append(user)
                        return user
                    else:
                        logger.warning("[HIVENCLIENT] Failed to request user data from the Hiven-API!")
                        return cached_user
                else:
                    logger.warning("[HIVENCLIENT] Failed to request user data from the Hiven-API!")
                    return cached_user
            else:
                return None

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to get User based with id {user_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def get_room(self, room_id: int) -> typing.Union[types.Room, None]:
        """
        Returns a Hiven Room Object based on the passed room ID.

        :param room_id: The id of the room that should be fetched
        :return: The Room Object if it was found
        """
        try:
            cached_room = utils.get(self.rooms, id=room_id)
            if cached_room:
                return cached_room

                # house = cached_room.house
                #
                # raw_data = await self.connection.http.request(endpoint=f"/rooms/{room_id}")
                # # Currently not possible to request room data from Hiven!
                # # Therefore only cached rooms can be accessed at the moment!
                # if raw_data:
                #     data = raw_data.get('data')
                #     if data:
                #         room = await types.Room.from_dict(data, self.connection.http, house=house)
                #         # Removing the older cached room
                #         self.connection._rooms.remove(cached_room)
                #         # Appending the data to the client cache
                #         self.connection._rooms.append(room)
                #         return room
                #     else:
                #         logger.warning("[HIVENCLIENT] Failed to request room data from the Hiven-API!")
                #         return cached_room
                # else:
                #     logger.warning("[HIVENCLIENT] Failed to request room data from the Hiven-API!")
                #     return cached_room
            else:
                return None

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to get Room with id {room_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def get_private_room(self, room_id: float) -> typing.Union[types.PrivateRoom, None]:
        """
        Returns a Hiven PrivateRoom or GroupChatRoom Object based on the passed room ID.

        :return: The Private Room Object if it was found
        """
        try:
            cached_private_room = utils.get(self.private_rooms, id=room_id)
            if cached_private_room:
                return cached_private_room

                # raw_data = await self.connection.http.request(endpoint=f"/rooms/{room_id}")
                # # Currently not possible to request room data from Hiven!
                # # Therefore only cached rooms can be accessed at the moment!
                # if raw_data:
                #     data = raw_data.get('data')
                #     if data:
                #         room = await types.PrivateRoom.from_dict(data, self.connection.http)
                #
                #         # Appending the data to the client cache
                #         self.connection._private_rooms.remove(cached_private_room)
                #         self.connection._private_rooms.append(room)
                #         return room
                #     else:
                #         logger.warning("[HIVENCLIENT] Failed to request private_room data from the Hiven-API!")
                #         return cached_private_room
                # else:
                #     logger.warning("[HIVENCLIENT] Failed to request private_room data from the Hiven-API!")
                #     return cached_private_room
            else:
                return None

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to get Private Room with id {room_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def create_house(self, name: str) -> types.LazyHouse:
        """
        Creates a new house on Hiven if the limit is not yet reached

        Note! The returned house does not have all the necessary data and only the basic data!
        To get the regular house use `utils.get(client.houses, ID=house_id)`

        :return: A low-level form of the House object!
        """
        try:
            resp = await self.connection.http.post(
                endpoint="/houses",
                json={'name': name})

            if resp.status < 300:
                raw_data = await resp.json()
                if raw_data:
                    data = raw_data.get('data')
                    if data:
                        lazy_house = await types.LazyHouse.from_dict(data, self.http, self.rooms)
                        return lazy_house
                    else:
                        raise errs.HTTPReceivedNoDataError()
                else:
                    raise errs.HTTPReceivedNoDataError()
            else:
                raise errs.HTTPFailedRequestError()

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to create House: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def delete_house(self, house_id: int) -> typing.Union[int, None]:
        """
        Deletes a house based on passed ID on Hiven
        :param house_id: ID of the house
        :return: Returns the ID of the House if successful
        """
        try:
            cached_house = utils.get(self.houses, id=utils.convert_value(int, house_id))
            if cached_house:
                resp = await self.connection.http.delete(endpoint=f"/houses/{house_id}")

                if resp.status < 300:
                    return self.user.id
                else:
                    raise errs.HTTPFailedRequestError()
            else:
                logger.warning(f"[HIVENCLIENT] The house with id {house_id} does not exist in the client cache!")
                return None

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to delete House: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def fetch_invite(self, invite_code: str) -> typing.Union[types.Invite, None]:
        """
        Fetches an invite from Hiven

        :param invite_code: Invite Code for the Invite
        :return: An Invite Instance
        """
        try:
            raw_data = await self.connection.http.request(endpoint=f"/invites/{invite_code}")

            data = raw_data.get('data')
            if data:
                return await types.Invite.from_dict(data, self.connection.http, houses=self.houses)
            else:
                raise errs.HTTPReceivedNoDataError()

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to fetch the invite with invite_code '{invite_code}': \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def get_feed(self) -> typing.Union[types.Feed, None]:
        """
        Get the current users feed

        :return: A Feed Instance
        """
        try:
            raw_data = await self.connection.http.request(endpoint=f"/streams/@me/feed")

            if raw_data:
                data = raw_data.get('data')
                if data:
                    return types.Feed(data, self.connection.http)
                else:
                    raise errs.HTTPReceivedNoDataError()
            else:
                raise errs.HTTPReceivedNoDataError()

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to get the users feed: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def get_mentions(self) -> typing.Union[list, types.Mention]:
        """
        Gets all mentions of the client user
        
        :return: A list of all Mention Objects
        """
        try:
            raw_data = await self.connection.http.request(endpoint=f"/streams/@me/mentions")

            data = raw_data.get('data')
            if data:
                mention_list = []
                for msg_data in data:
                    room = utils.get(self.rooms, id=utils.convert_value(int, msg_data.get('room_id')))
                    message = await types.Message.from_dict(
                        msg_data,
                        self.connection.http,
                        house_=room.house,
                        room_=room,
                        author=self.user)
                    mention_list.append(message)

                return mention_list
            else:
                raise errs.HTTPReceivedNoDataError()

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to get the users mentions: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def change_room_settings(self,
                                   room: typing.Union[int, types.Room],
                                   **kwargs) -> typing.Union[types.Room, None]:
        """
        Changed a room settings if permission are sufficient!

        Available options:

        notification_preference - Notification preference for the room. 0 = 'all'/1 = 'mentions'/2 = 'none'

        :param room: Room object that should be modified
        :return: The `Room` object if the request was successful else None
        """
        try:
            if type(room) is int:
                room_id = room
            elif type(room) is types.User:
                room_id = getattr(room, 'id')
            else:
                raise TypeError(f"Expected User or int! Not {type(room)}")

            json = {}
            for key in kwargs:
                # Searching through the possible keys and adding them if they are found!
                if key in ['notification_preference', 'name']:
                    json[key] = kwargs.get(key)

            resp = await self.connection.http.put(
                endpoint=f"/users/@me/settings/room_overrides/{room_id}",
                json=json)

            if resp.status < 300:
                return utils.get(self.rooms, id=room_id)
            else:
                raise errs.HTTPFailedRequestError()

        except Exception as e:
            room_id = room if room is not None else getattr(room, 'id', None)
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to edit the room with id {room_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def create_private_room(self,
                                  user: typing.Union[int, types.User] = None) -> typing.Union[types.PrivateRoom, None]:
        """
 
        Adds a user to a private chat room where you can send messages.
        
        Planned: Called when trying to send a message to a user and not room exists yet

        ---

        :param user: Int or User Object used for the request
        :return: The created PrivateRoom if the request was successful else None
        """
        try:
            if type(user) is int:
                user_id = str(user)  # ID must be in string format
            elif type(user) is types.User:
                user_id = str(getattr(user, 'id'))  # ID must be in string format
            else:
                raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.connection.http.post(endpoint="/users/@me/rooms",
                                                   json={'recipient': user_id})
            if resp.status < 300:
                raw_data = await resp.json()
                data = raw_data.get('data')
                if data:
                    private_room = await types.PrivateRoom.from_dict(data, self.connection.http)
                    # Adding the PrivateRoom to the Cache
                    self.connection._private_rooms.append(private_room)
                    return private_room
                else:
                    raise errs.HTTPReceivedNoDataError()
            else:
                raise errs.HTTPFailedRequestError()

        except Exception as e:
            user_id = user if user is not None else getattr(user, 'id', None)
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to create private_room with user with the id={user_id}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None

    async def create_private_group_room(self,
                                        recipients: typing.List[typing.Union[int, types.User]] = [],
                                        ) -> typing.Union[types.PrivateGroupRoom, None]:
        """
        Adds the passed users to a private group chat room where you can send messages.

        :param recipients: List of recipients
        :return: The created PrivateGroupRoom if the request was successful else None
        """
        try:
            user_ids = []
            for user in recipients:
                if type(user) is int:
                    user_ids.append(str(user))  # ids must be in string format
                elif type(user) is types.User:
                    user_ids.append(str(getattr(user, 'id')))  # ids must be in string format
                else:
                    raise TypeError(f"Expected User or int! Not {type(user)}")

            resp = await self.connection.http.post(endpoint="/users/@me/rooms", json={'recipients': user_ids})
            if resp.status < 300:
                raw_data = await resp.json()
                data = raw_data.get('data')
                if data:
                    private_room = await types.PrivateGroupRoom.from_dict(data,
                                                                          self.connection.http,
                                                                          users=self.users,
                                                                          client_user=self.user)

                    # Adding the PrivateGroupRoom to the Cache
                    self.connection._private_rooms.append(private_room)
                    return private_room
                else:
                    raise errs.HTTPReceivedNoDataError()
            else:
                raise errs.HTTPFailedRequestError()

        except Exception as e:
            utils.log_traceback(msg="[HIVENCLIENT] Traceback:",
                                suffix=f"Failed to send a friend request a user with ids={recipients}: \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            return None
