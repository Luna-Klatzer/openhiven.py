import asyncio
import time
import sys
import os
import json
import logging
from typing import Optional
import aiohttp

import openhivenpy.types as types
import openhivenpy.exceptions as errs
import openhivenpy.utils as utils
from openhivenpy.events import EventHandler
from openhivenpy.types import Client

__all__ = ('API', 'Websocket')

logger = logging.getLogger(__name__)


class API:
    """`openhivenpy.gateway`

    API
    ~~~

    API Class for interaction with the Hiven API not depending on the HTTP

    Will soon either be repurposed or removed!

    """

    @property
    def host(self):
        return "https://api.hiven.io/v1"


class Websocket(Client, API):
    """`openhivenpy.gateway.Websocket`

    Websocket
    ~~~~~~~~~

    Websocket Class that will listen to the Hiven Websocket and trigger user-specified events.

    Calls `openhivenpy.EventHandler` and will execute the user code if registered

    Is directly inherited into connection and cannot be used as a standalone class!

    The Websocket class handles the websocket connection to Hiven and will react to the Events frames that are received.
    It will automatically handle handshakes as well as ping-pong interactions with the server and

    Parameter:
    ----------

    restart: `bool` - If set to True the process will restart if an exception occurred

    host: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'api.hiven.io'

    api_version: `str` - Version string for the API Version. Defaults to 'v1'

    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128,
                    is None or is empty!

    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`

    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake didn't complete
                            successfully. Defaults to `20`

    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.

    event_handler: 'openhivenpy.events.EventHandler` - Handler for Websocket Events

    """

    def __init__(
            self,
            *,
            event_handler: EventHandler,
            event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop(),
            **kwargs):

        self._HOST = kwargs.get('api_url', os.getenv("HIVEN_HOST"))
        self._API_VERSION = kwargs.get('api_version', os.getenv("HIVEN_API_VERSION"))

        self._WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self._ENCODING = "json"

        # In milliseconds
        _env_heartbeat = int(os.getenv("CONNECTION_HEARTBEAT"))
        self._HEARTBEAT = kwargs.get('heartbeat', _env_heartbeat)
        self._TOKEN = kwargs.get('token', None)

        self._close_timeout = kwargs.get('close_timeout', int(os.getenv("CLOSE_TIMEOUT")))

        self._event_handler = event_handler
        self._event_loop = event_loop

        self._restart = kwargs.get('restart', False)
        self._log_ws_output = kwargs.get('log_ws_output', False)

        self._CUSTOM_HEARTBEAT = False if self._HEARTBEAT == _env_heartbeat else True
        self._ws_session = None
        self._ws = None
        self._connection = None
        self._lifesignal = None

        # Websocket and Connection Attribute
        self._open = False

        self._connection_start = None
        self._startup_time = None
        self._initialized = False
        self._ready = False
        self._connection_start = None

        self._connection_status = "CLOSED"

        # client data is inherited here and will be then passed to the connection class
        super().__init__()

    @property
    def open(self):
        return self._open

    @property
    def closed(self):
        return self._ws.closed

    @property
    def close_timeout(self) -> int:
        return self._close_timeout

    @property
    def websocket_url(self) -> str:
        return self._WEBSOCKET_URL

    @property
    def encoding(self) -> str:
        return self._ENCODING

    @property
    def heartbeat(self) -> int:
        return self._HEARTBEAT

    @property
    def ws_session(self) -> aiohttp.ClientSession:
        return self._ws_session

    @property
    def ws(self):
        return self

    @property
    def ws_connection(self) -> asyncio.Task:
        return self._connection

    # Starts the connection over a new websocket
    async def ws_connect(self, session: aiohttp.ClientSession, heartbeat: int = None) -> None:
        """`openhivenpy.gateway.Websocket.connect()`

        Creates a connection to the Hiven API.

        Not supposed to be called by the user!

        Consider using HivenClient.connect() or HivenClient.run()

        """
        self._HEARTBEAT = heartbeat if heartbeat is not None else self._HEARTBEAT
        self._ws_session = session

        async def ws_connection():
            """
            Connects to Hiven using the http-session that was created prior during
            startup. The websocket will then interact with Hiven and await responses
            and react with pongs on pings. Will send lifesignals over the pre-set
            Heartbeat to ensure the connection stays alive and does not time-out.

            """
            try:
                async with session.ws_connect(
                        url=self._WEBSOCKET_URL,
                        timeout=self._close_timeout,
                        autoping=True,
                        autoclose=True,
                        heartbeat=self._HEARTBEAT,
                        receive_timeout=None,
                        max_msg_size=0) as ws:

                    self._ws = ws
                    self._connection_status = "OPEN"
                    self._open = True

                    await asyncio.gather(self._event_handler.ev_connection_start(),
                                         self.lifesignal(ws),
                                         self.response_handler(ws=ws))

            except KeyboardInterrupt:
                pass

            except Exception as e:
                logger.critical(f"[WEBSOCKET] >> The connection to Hiven failed to be kept alive or started! "
                                f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

                # Closing
                close = getattr(self, "close", None)
                if callable(close):
                    await close(exec_loop=not self._restart, reason="WS encountered an error!", restart=self._restart)

                return

            finally:
                self._open = False
                return

        # Creating a task that wraps the coroutine
        self._connection = self._event_loop.create_task(ws_connection())

        # Running the task in the background
        try:
            await self._connection
        except KeyboardInterrupt:
            pass
        # Avoids that the user notices that the task was cancelled! aka. Silent Error
        except asyncio.CancelledError:
            logger.debug("[WEBSOCKET] << The websocket Connection to Hiven unexpectedly stopped!"
                         "Probably caused by an error or automatic/forced closing!")
        except Exception as e:
            logger.critical(e)
            raise errs.GatewayException(f"[WEBSOCKET] << Exception in main-websocket process!"
                                        f"Cause of error{sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return

    # Loop for receiving messages from Hiven
    async def response_handler(self, ws) -> None:
        """`openhivenpy.gateway.Websocket.ws_receive_response()`

        Handler for Swarm responses

        Not supposed to be called by a user!

        """
        try:
            # Response Handler for the websocket that will on errors, responses, pings and pongs
            # react and trigger events over the event_resp_handler which will trigger events.
            # The function will break if a close frame was received and then automatically
            # close the connection. This is then only way the connection can normally close
            # except user forced close or a raised exceptions while processing.
            while self.open:
                msg = await ws.receive()
                if msg is not None:
                    logger.debug(f"[WEBSOCKET] << Got Type {msg.type}")
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            resp = msg.json()
                        except Exception:
                            resp = None

                        if resp.get('op', 0) == 1:
                            logger.info("[WEBSOCKET] >> Connection to Hiven Swarm established")
                            # Authorizing with token
                            logger.info("[WEBSOCKET] >> Authorizing with token")
                            await ws.send_str(str(json.dumps({"op": 2, "d": {"token": str(self._TOKEN)}})))

                            if self._CUSTOM_HEARTBEAT is False:
                                self._HEARTBEAT = resp['d']['hbt_int']
                                ws.heartbeat = self._HEARTBEAT

                            logger.debug(f"[WEBSOCKET] >> Heartbeat set to {ws.heartbeat}")
                            logger.info("[WEBSOCKET] << Connection to Hiven Swarm established")
                        else:
                            if msg.data == 'close cmd':
                                logger.debug("[WEBSOCKET] << Received close frame!")
                                break

                            if self._log_ws_output:
                                logger.debug(f"[WEBSOCKET] << Received: {str(resp)}")

                            await self._event_resp_handler(resp)

                    elif msg.type == aiohttp.WSMsgType.CLOSE:
                        logger.debug(f"[WEBSOCKET] << Received close frame with msg='{msg.extra}'!")
                        break

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.critical(f"[WEBSOCKET] Failed to handle response >> {ws.exception()} >>{msg}")
                        raise errs.WSFailedToHandle(msg.data)
                await asyncio.sleep(0.01)
        finally:
            if not ws.closed:
                await ws.close()
            logger.info(f"[WEBSOCKET] << Connection to Remote ({self._WEBSOCKET_URL}) closed!")
            self._open = False

            # Closing
            close = getattr(self, "close", None)
            if callable(close):
                await close(exec_loop=True, reason="Response Handler stopped!", restart=self._restart)

            return

    async def lifesignal(self, ws) -> None:
        """`openhivenpy.gateway.Websocket.ws_lifesignal()`

        Handler for Opening the Websocket.

        Not supposed to be called by a user!

        """
        try:
            # Life Signal that sends an op-code to Hiven to signalise the connection is still alive
            # Will automatically break if the connection is supposed to be CLOSING or CLOSED
            # Very unlikely to happen to due to prior force closing or self._open closing itself
            # which already stops the entire websocket task
            async def _lifesignal():
                while self._open:
                    await asyncio.sleep(self._HEARTBEAT / 1000)

                    logger.debug(f"[WEBSOCKET] >> Lifesignal at {time.time()}")
                    await ws.send_str(str(json.dumps({"op": 3})))

                    if self._connection_status in ["CLOSING", "CLOSED"]:
                        break
                return

            self._connection_status = "OPEN"
            self._lifesignal = asyncio.create_task(_lifesignal())
            await self._lifesignal
            return

        except asyncio.CancelledError:
            return

    # Event Triggers
    async def _event_resp_handler(self, resp_data):
        """`openhivenpy.gateway.Websocket.ws_on_response()`

        Handler for the Websocket events and the message data.

        Not supposed to be called by a user!

        """
        try:
            response_data = resp_data.get('d', {})
            swarm_event = resp_data.get('e', "")

            logger.debug(f"Received Event {swarm_event}")

            if not hasattr(self, '_houses') and not hasattr(self, '_users'):
                logger.error("[WEBSOCKET] << The client attributes _users and _houses do not exist!"
                             "The class might be initialized faulty!")
                raise errs.FaultyInitialization("The client attributes _users and _houses do not exist!"
                                                "The class might be initialized faulty!")

            if swarm_event == "INIT_STATE":
                """ 
                Authorization was successful and client data is received
                
                Json-Data:
                op: 0
                d: {
                  user: {
                    username: string,
                    user_flags: string,
                    name: string,
                    id: string,
                    icon: string,
                    header: string,
                    presence: string
                  },
                  settings: {
                    user_id: string,
                    theme: null,
                    room_overrides: {
                      id: { notification_preference: int }
                    },
                    onboarded: unknown,
                    enable_desktop_notifications: unknown
                  },
                  relationships: {
                    id: {
                      user_id: string,
                      user: {
                        username: string,
                        user_flags: string,
                        name: string,
                        id: string,
                        icon: string,
                        header: string,
                        presence: string
                      },
                      type: int,
                      last_updated_at: string
                    }
                  },
                  read_state: {
                    id: {
                      message_id: string,
                      mention_count: int
                    },
                  },
                  private_rooms: room[]
                  presences: {
                    id: {
                      username: string,
                      user_flags: string,
                      name: string,
                      id: string,
                      icon: string,
                      header: string,
                      presence: string
                    }
                  },
                  house_memberships: {
                    id: {
                      user_id: string,
                      user: {
                        username: string,
                        user_flags: string,
                        name: string,
                        id: string,
                        icon: string,
                        header: string,
                        presence: string
                      },
                      roles: array,
                      last_permission_update: string,
                      joined_at: string,
                      house_id: string
                    }
                  },
                  house_ids: string[]
                }
                """
                await super().init_meta_data(response_data)

                init_time = time.time() - self._connection_start
                await self._event_handler.ev_init_state(time=init_time)
                self._initialized = True

            elif swarm_event == "HOUSE_JOIN":
                """
                The Client joined a house
                
                Json-Data:
                op: 0
                d: {
                  rooms: room[{
                    type: int,
                    recipients: null
                    position: int,
                    permission_overrides: bits,
                    owner_id: string,
                    name: string,
                    last_message_id: string,
                    id: string,
                    house_id: string,
                    emoji: object,
                    description: string,
                    default_permission_override: int
                  }],
                  roles: role[{
                    position: int,
                    name: string,
                    level: int,
                    id: string,
                    deny: bits,
                    color: string,
                    allow: bits
                  }],
                  owner_id: string,
                  name: string,
                  members: [{
                    user_id: string,
                    user: {
                      username: string,
                      user_flags: string,
                      name: string,
                      id: string,
                      icon: string,
                      header: string,
                      presence: string
                    },
                    roles: array,
                    last_permission_update: string,
                    joined_at: string,
                    house_id: string
                  }],
                  id: string,
                  icon: string,
                  entities: [{
                    type: int,
                    resource_pointers: [{
                      resource_type: string,
                      resource_id: string
                    }],
                    position: int,
                    name: string,
                    id: string
                  }],
                  default_permissions: int,
                  banner: string
                }
                """
                # Creating a house object that will then be appended
                house = types.House(response_data, self.http, super().id)
                cached_house = utils.get(self._houses, id=int(response_data.get('id', 0)))
                # Removing if a house exists with the same id to ensure the newest house is available
                if cached_house:
                    self._houses.remove(cached_house)

                for usr in response_data['members']:
                    user = utils.get(self._users, id=usr['id'] if hasattr(usr, 'id') else usr['user']['id'])
                    if user is None:
                        # Appending to the client users list
                        self._users.append(types.User(usr, self.http))

                        # Appending to the house users list
                        usr = types.Member(usr, self._TOKEN, house)
                        house._members.append(usr)

                for room in response_data.get('rooms'):
                    self._rooms.append(types.Room(room, self.http, house))

                # Appending to the client houses list
                self._houses.append(house)
                asyncio.create_task(self._event_handler.ev_house_join(house))

            elif swarm_event == "HOUSE_LEAVE":
                """
                The client leaves a house
                
                Json-Data:
                op: 0
                d: {
                  id: string,
                  house_id: string
                }
                """
                house = utils.get(self._houses, id=int(response_data.get('house_id')))
                self._houses.remove(house)
                asyncio.create_task(self._event_handler.ev_house_exit(house=house))

            elif swarm_event == "HOUSE_DOWN":
                """
                A house is unreachable
                
                Json-Data:
                op: 0
                d: {
                  unavailable: boolean,
                  house_id: string
                }
                """
                t = time.time()
                house = utils.get(self._houses, id=int(response_data.get('house_id', 0)))
                logger.debug(f"[WEBSOCKET] << Downtime of '{house.name}' reported! "
                            "House was either deleted or is currently unavailable!")
                asyncio.create_task(self._event_handler.ev_house_down(time=t, house=house))

            elif swarm_event == "HOUSE_MEMBER_ENTER":
                """
                A user joined a house
                
                Json-Data:
                op: 0
                d: {
                  user_id: string,
                  user: {
                      username: string,
                      user_flags: string,
                      name: string,
                      id: string,
                      icon: string,
                      bot: bool,
                  },
                  roles: [],
                  presence: string,
                  last_permission_update: null,
                  joined_at: string,
                  id: string,
                  house_id: string
                }
                """
                if self._ready:
                    house_id = response_data.get('house_id')
                    if house_id is None:
                        house_id = response_data.get('house', {}).get('id', 0)
                    house = utils.get(self._houses, id=int(house_id))

                    # Removing the old user and appending the new data so it's up-to-date
                    user_id = response_data.get('user_id')
                    if user_id is None:
                        user_id = response_data.get('user', {}).get('id', 0)
                    cached_user = utils.get(self._users, id=int(user_id))
                    if response_data.get('user') is not None:
                        user = types.User(response_data['user'], self.http)

                        if cached_user:
                            self._users.remove(cached_user)
                        self._users.append(user)
                    else:
                        user = cached_user

                    # Removing the old member and appending the new data so it's up-to-date
                    cached_member = utils.get(house._members, user_id=int(response_data.get('user_id', 0)))
                    if response_data.get('user') is not None:
                        member = types.Member(response_data['user'], self.http, house)

                        if cached_member:
                            house._members.remove(cached_member)
                        house._members.append(member)
                    else:
                        member = cached_user

                    asyncio.create_task(self._event_handler.ev_house_member_enter(member, house))

            elif swarm_event == "HOUSE_MEMBER_UPDATE":
                """
                A member data was updated. (role update, permission update, nick etc.)
                
                Json-Data:
                op: 0
                d: {
                  user_id: string,
                  user: {
                    website: string,
                    username: string,
                    user_flags: int,
                    name: string,
                    location: string,
                    id: string,
                    icon: string,
                    header: string,
                    email_verified: boolean,
                    bot: boolean,
                    bio: string
                  },
                  roles: object[],
                  presence: string,
                  last_permission_update: unknown,
                  joined_at: string,
                  id: string,
                  house_id: string
                }
                """
                if self._ready:
                    house = utils.get(self._houses, id=int(response_data.get('house_id', 0)))

                    # Removing the old user and appending the new data so it's up-to-date
                    cached_user = utils.get(self._users, id=int(response_data.get('user_id', 0)))
                    if response_data.get('user') is not None:
                        user = types.User(response_data['user'], self.http)

                        if cached_user:
                            self._users.remove(cached_user)
                        self._users.append(user)

                    # Removing the old member and appending the new data so it's up-to-date
                    cached_member = utils.get(house._members, user_id=int(response_data.get('user_id', 0)))
                    if response_data.get('user') is not None:
                        member = types.Member(response_data['user'], self.http, house)

                        if cached_member:
                            house._members.remove(cached_member)
                        house._members.append(member)
                    else:
                        member = cached_user

                    asyncio.create_task(self._event_handler.ev_house_member_update(member, house))

            elif swarm_event == "HOUSE_MEMBER_EXIT":
                """
                A member left a house
                
                Json-Data:
                op: 0
                d: {
                    id: string,
                    house_id: string
                }
                """
                user = types.User(response_data, self.http)

                asyncio.create_task(self._event_handler.ev_house_member_exit(user))

            elif swarm_event == "PRESENCE_UPDATE":
                """
                A user presence was updated
                
                Json-Data:
                op: 0
                d: {
                  username: string,
                  user_flags: string,
                  name: string,
                  id: string,
                  icon: string,
                  header: string,
                  presence: string
                }
                """
                user = types.User(response_data, self.http)
                presence = types.Presence(response_data, user, self.http)
                asyncio.create_task(self._event_handler.ev_presence_update(presence, user))

            elif swarm_event == "MESSAGE_CREATE":
                """
                A user created a message
                
                Json-Data:
                op: 0
                d: {
                  timestamp: int,
                  room_id: string,
                  mentions: [{
                    username: string,
                    user_flags: string,
                    name: string,
                    id: string,
                    icon: string,
                    header: string,
                    presence: string,
                    bot: boolean
                  }],
                  member: {
                    user_id: string,
                    user: {
                      username: string,
                      user_flags: string,
                      name: string,
                      id: string,
                      icon: string,
                      header: string,
                      presence: string
                    },
                    roles: array,
                    last_permission_update: string,
                    joined_at: string,
                    house_id: string
                  },
                  id: string,
                  house_id: string,
                  exploding_age: int,
                  exploding: boolean,
                  device_id: string,
                  content: string,
                  bucket: int,
                  author_id: string,
                  author: {
                    username: string,
                    user_flags: string,
                    name: string,
                    id: string,
                    icon: string,
                    header: string,
                    presence: string
                  }
                  attachment: {
                    media_url: string,
                    filename: string,
                    dimensions: {
                      width: int,
                      type: string,
                      height: int
                    }
                  }
                }
                """
                if self._ready:
                    if response_data.get('house_id') is not None:
                        house = utils.get(self._houses, id=int(response_data.get('house_id', 0)))
                    else:
                        house = None

                    # Updating the last message id in the Room
                    room = utils.get(self._rooms, id=int(response_data.get('room_id', 0)))
                    self._rooms.remove(room)
                    room._last_message_id = response_data.get('id')
                    self._rooms.append(room)

                    # Removing the old user and appending the new data so it's up-to-date
                    cached_author = utils.get(self._users, id=int(response_data.get('author_id', 0)))
                    if response_data.get('author') is not None:
                        author = types.User(response_data['author'], self.http)

                        if cached_author:
                            self._users.remove(cached_author)
                        self._users.append(author)
                    else:
                        author = cached_author

                    message = types.Message(response_data, self.http, house, room, author)
                    asyncio.create_task(self._event_handler.ev_message_create(message))

            elif swarm_event == "MESSAGE_DELETE":
                """
                A user deleted a message
                
                Json-Data:
                op: 0
                d: {
                  room_id: string,
                  message_id: string,
                  house_id: string
                }
                """
                message = types.DeletedMessage(response_data)
                asyncio.create_task(self._event_handler.ev_message_delete(message))

            elif swarm_event == "MESSAGE_UPDATE":
                """
                User edited message update
                
                Json-Data:
                op: 0
                d: {
                  type: int,
                  timestamp: string,
                  room_id: string,
                  metadata: unknown,
                  mentions: [{
                    username: string,
                    user_flags: string,
                    name: string,
                    id: string,
                    icon: string,
                    header: string,
                    presence: string
                  }],
                  id: string,
                  house_id: string,
                  exploding_age: int,
                  exploding: boolean,
                  embed: object,
                  edited_at: string,
                  device_id: string,
                  content: string,
                  bucket: int,
                  author_id: string,
                  attachment: {
                    media_url: string,
                    filename: string,
                    dimensions: {
                      width: int,
                      type: string,
                      height: int
                    }
                  }
                }
                """
                if self._ready:
                    if response_data.get('house_id') is not None:
                        house = utils.get(self._houses, id=int(response_data.get('house_id', 0)))
                    else:
                        house = None

                    room = utils.get(self._rooms, id=int(response_data.get('room_id', 0)))

                    cached_author = utils.get(self._users, id=int(response_data.get('author_id', 0)))
                    if response_data.get('author') is not None:
                        author = types.User(response_data['author'], self.http)

                        if cached_author:
                            self._users.remove(cached_author)
                        self._users.append(author)
                    else:
                        author = cached_author

                    message = types.Message(response_data, self.http, house=house, room=room, author=author)
                    asyncio.create_task(self._event_handler.ev_message_update(message))

            elif swarm_event == "TYPING_START":
                """
                User started typing
                
                Json-Data:
                op: 0
                d: {
                  timestamp: int,
                  room_id: string,
                  house_id: string,
                  author_id: string
                }
                """
                room = utils.get(self._rooms, id=int(response_data.get('room_id', 0)))
                house = utils.get(self._houses, id=int(response_data.get('house_id', 0)))
                member = utils.get(house.members, id=int(response_data.get('author_id', 0)))
                typing = types.Typing(response_data, member, room, house, self.http)
                asyncio.create_task(self._event_handler.ev_typing_start(typing))

            elif swarm_event == "TYPING_END":
                """
                Typing of a user ended
                
                Currently not existing!
                
                Json-Data:
                """
                room = utils.get(self._rooms, id=int(response_data.get('room_id', 0)))
                house = utils.get(self._houses, id=int(response_data.get('room_id', 0)))
                member = utils.get(house.members, id=int(response_data.get('room_id', 0)))
                member = types.Typing(response_data, member, room, house, self.http)
                asyncio.create_task(self._event_handler.ev_typing_end(member))

            # In work
            elif swarm_event == "HOUSE_MEMBERS_CHUNK":
                """
                For requesting house member states
                
                Json-Data:
                op: 0
                d: {
                  members: {
                    id: {
                      user_id: string,
                      user: {
                        username: string,
                        user_flags: string,
                        name: string,
                        id: string,
                        icon: string,
                        header: string,
                        presence: string
                      },
                      roles: array,
                      last_permission_update: string,
                      joined_at: string,
                      house_id: string
                    }
                  },
                  house_id: string
                }
                """
                data = response_data
                asyncio.create_task(self._event_handler.ev_house_member_chunk(data=data))

            elif swarm_event == "BATCH_HOUSE_MEMBER_UPDATE":
                """
                Multiple updates of members that are stacked
                
                Json-Data:
                {
                  house_id: string;
                  batch_type: list;
                  batch_size: int;
                  data: {
                    [resource_id: string]: HouseMember
                  }
                }
                """
                data = response_data
                asyncio.create_task(self._event_handler.ev_batch_house_member_update(data=data))

            elif swarm_event == "HOUSE_ENTITIES_UPDATE":
                """
                House was updated
                
                Json-Data:
                op: 0
                d: {
                  house_id: '182410583881021247',
                  entities: [{
                    type: int,
                    resource_pointers: [{
                      resource_type: string,
                      resource_id: string
                    }],
                    position: int,
                    name: string,
                    id: string
                  }]
                }
                """
                pass

            elif swarm_event == "RELATIONSHIP_UPDATE":
                """
                Relationship between two users was updated
                
                Json-Data:
                op: 0
                d: {
                  user: {
                    website: string,
                    username: string,
                    user_flags: int,
                    name: string,
                    location: string,
                    id: string,
                    icon: string,
                    bio: string
                  },
                  type: int,
                  recipient_id: string,
                  id: string
                }
                """
                data = response_data
                relationship = types.Relationship(data, self.http)
                asyncio.create_task(self._event_handler.ev_relationship_update(relationship))
            else:
                logger.debug(f"[WEBSOCKET] << Unknown Event {swarm_event} without Handler")

        except Exception as e:
            logger.debug(f"[WEBSOCKET] << Failed to handle Event in the websocket! "
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return
