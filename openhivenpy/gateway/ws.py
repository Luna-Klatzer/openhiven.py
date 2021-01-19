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

__all__ = ['Websocket']

logger = logging.getLogger(__name__)


class Websocket(Client):
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
                            successfully. Defaults to `40`

    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.

    event_handler: 'openhivenpy.events.EventHandler` - Handler for Websocket Events

    """

    def __init__(
            self,
            *,
            event_handler: EventHandler,
            event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
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
        super().__init__()

    @property
    def open(self):
        return self._open

    @property
    def closed(self):
        return not self._ws.open

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
                                f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

                # Closing
                close = getattr(self, "close", None)
                if callable(close):
                    await close(exec_loop=not self._restart, reason="WS encountered an error!", restart=self._restart)

                return

            finally:
                self._open = False
                return

        # Creating a task that wraps the coroutine
        self._connection = asyncio.create_task(ws_connection())

        # Running the task in the background
        try:
            await self._connection
        except KeyboardInterrupt:
            pass
        # Avoids that the user notices that the task was cancelled! aka. Silent Error
        except asyncio.CancelledError:
            logger.debug("[WEBSOCKET] << The websocket Connection to Hiven unexpectedly stopped and was cancelled! "
                         "Likely caused due to an error or automatic/forced closing!")
        except Exception as e:
            logger.debug("[WEBSOCKET] << The websocket Connection to Hiven unexpectedly stopped and failed to process "
                         f"> {e}!")

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
                            else:
                                if self._log_ws_output:
                                    logger.debug(f"[WEBSOCKET] << Received: {str(resp)}")

                                if resp.get('e') == "INIT_STATE":
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
                                    await super().init_meta_data(resp.get('d'))

                                    init_time = time.time() - self._connection_start
                                    self._initialized = True
                                    await self._event_handler.ev_init_state(time=init_time)

                                await asyncio.create_task(self._event_resp_handler(resp))

                    elif msg.type == aiohttp.WSMsgType.CLOSE:
                        logger.debug(f"[WEBSOCKET] << Received close frame with msg='{msg.extra}'!")
                        break

                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.critical(f"[WEBSOCKET] Failed to handle response >> {ws.exception()} >>{msg}")
                        raise errs.WSFailedToHandle(msg.data)

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

            if swarm_event == "INIT_STATE":
                logger.info("[WEBSOCKET] >> Initialization of Client was successful!")

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
                if self._initialized:
                    async def house_join_handler():
                        """
                        Handler for the house_join event of the connected client which will trigger
                        the on_house_add event and return as parameter the house.
                        """
                        data = response_data

                        # Creating a house object that will then be appended
                        house = types.House(data, self.http, self.id)
                        cached_house = utils.get(self._houses, id=int(data.get('id', 0)))
                        # Removing a cached house if it exists
                        if cached_house:
                            self._houses.remove(cached_house)
                            logger.warning("[HOUSE_LEAVE] Removed cached house with same id on_house_add. "
                                           "Possibly old or faulty Client data!")

                        if data.get('members') is None:
                            logger.warning("[HOUSE_LEAVE] Got empty members list in on_house_add!")
                        else:
                            for usr in data['members']:
                                if hasattr(usr, 'id'):
                                    user_id = int(usr.get('id', 0))
                                else:
                                    user_id = int(usr['user'].get('id', 0))

                                # Getting the user from the list if it exists
                                user = utils.get(self._users, id=user_id)
                                # If it doesn't exist it needs to be added to the list
                                if user is None:
                                    # Appending to the client users list
                                    self._users.append(types.User(usr, self.http))

                            for room in response_data['rooms']:
                                self._rooms.append(types.Room(room, self.http, house))

                        # Appending to the client houses list
                        self._houses.append(house)

                        # Creating a new task for handling the event
                        # TODO! Needs error handling and name traceback and log!
                        asyncio.create_task(self._event_handler.ev_house_join(house))

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_join_handler())

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
                if self._initialized:
                    async def house_leave_handler():
                        """
                        Handler for the house_join event of the connected client which will
                        trigger on_house_remove and return as parameter the removed house.
                        """
                        house = utils.get(self._houses, id=int(response_data.get('house_id')))
                        if house:
                            # Removing the house
                            self._houses.remove(house)
                        else:
                            logger.debug("[HOUSE_LEAVE] Unable to locate left house in house cache! "
                                         "Possibly faulty Client data!")

                        # Creating a new task for handling the event
                        # TODO! Needs error handling and name traceback and log!
                        asyncio.create_task(self._event_handler.ev_house_exit(house=house))

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_leave_handler())

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
                if self._initialized:
                    async def house_down_handler():
                        """
                        Handler for downtime of a house! Triggers on_house_down and
                        returns as parameter the time of downtime and the house
                        """
                        data = response_data
                        t = time.time()
                        house = utils.get(self._houses, id=int(data.get('house_id', 0)))
                        if data.get('unavailable'):
                            logger.debug(f"[HOUSE_DOWN] << Downtime of '{house.name}' reported! "
                                         "House was either deleted or is currently unavailable!")
                        else:
                            pass

                        # Creating a new task for handling the event
                        # TODO! Needs error handling and name traceback and log!
                        asyncio.create_task(self._event_handler.ev_house_down(time=t, house=house))

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_down_handler())

            elif swarm_event == "HOUSE_MEMBER_ENTER":
                """
                A user joined a house or went online?
                
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
                if self._initialized:
                    async def house_member_enter():
                        """
                        Handler for a member joining a mutual house. Trigger on_house_enter
                        and returns as parameters the member obj and house obj.
                        """
                        try:
                            # Removing the old user and appending the new data so it's up-to-date
                            user_id = response_data.get('user_id')
                            if user_id is None:
                                # Backup is user id data
                                user_id = response_data.get('user', {}).get('id', 0)

                            # Getting the cached user
                            cached_user = utils.get(self._users, id=int(user_id))
                            if response_data.get('user') is not None:
                                user = types.User(response_data['user'], self.http)

                                if cached_user:
                                    # Removing old data
                                    self._users.remove(cached_user)

                                # Everything is fine
                                self._users.append(user)
                            else:
                                # If no user obj was sent the cached_user will server as the user
                                # Which can only be possible if the data is faulty and the user
                                # exists in another server
                                logger.warning("[HOUSE_MEMBER_ENTER] Got faulty ws event data with no existing user "
                                               "data!")
                                user = None

                            house_id = response_data.get('house_id')
                            if house_id is None:
                                house_id = response_data.get('house', {}).get('id', 0)
                            house = utils.get(self._houses, id=int(house_id))

                            # Checking if the house exits
                            if house:
                                cached_member = utils.get(house._members, user_id=int(response_data.get('user_id', 0)))
                                if response_data.get('user') is not None:
                                    member = types.Member(response_data['user'], house, self.http)

                                    if cached_member:
                                        # Removing old data
                                        house._members.remove(cached_member)

                                    # Everything is fine
                                    house._members.append(member)
                                else:
                                    # Falling back to the cached_user!
                                    if cached_member:
                                        member = None
                                        logger.warning("[HOUSE_MEMBER_ENTER] Got faulty ws event data with no "
                                                       "existing member data!")
                                    else:
                                        member = None
                                        logger.warning("[HOUSE_MEMBER_ENTER] Got faulty ws event data with no "
                                                       "existing member data!")

                            else:
                                logger.warning("[HOUSE_MEMBER_ENTER] Failed to add new member to unknown house! "
                                               "Possibly faulty client data!")
                                house = None
                                # Falling back to the user to provide some data
                                member = user
                                logger.warning("[HOUSE_MEMBER_ENTER] Event on_house_enter will have insufficient data! "
                                               ">> House object will default to None and member will default to cached "
                                               "user!")

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_house_member_enter(
                                member=member,
                                house=house
                            ))

                        except Exception as e:
                            logger.exception("[HOUSE_MEMBER_UPDATE] Failed to handle event and trigger "
                                             f"'on_member_update'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_member_enter())

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
                if self._initialized:
                    async def house_member_update_handler():
                        """
                        Handler for a house member update which will trigger on_member_update and return
                        as parameter the old member obj, the new member obj and the house.
                        """
                        try:
                            data = response_data
                            house = utils.get(self._houses, id=int(data.get('house_id', 0)))

                            # Removing the old user and appending the new data so it's up-to-date
                            cached_user = utils.get(self._users, id=int(data.get('user_id', 0)))
                            if data.get('user') is not None:
                                user = types.User(data['user'], self.http)

                                if cached_user:
                                    self._users.remove(cached_user)
                                self._users.append(user)
                            else:
                                user = None
                                logger.warning("[HOUSE_MEMBER_UPDATE] Got faulty ws event data with no "
                                               "existing member data!")
                                if not cached_user:
                                    logger.warning("[HOUSE_MEMBER_UPDATE] Unable to find user in the cache! "
                                                   f"USER_ID={data.get('user_id')}")

                            # Getting the cached member in the house if it exists
                            cached_member = utils.get(house._members, user_id=int(data.get('user_id', 0)))
                            if data.get('user') is not None:
                                member = types.Member(data['user'], house, self.http)

                                if cached_member:
                                    # Removing the old data
                                    house._members.remove(cached_member)
                                house._members.append(member)
                            else:
                                logger.warning("[HOUSE_MEMBER_UPDATE] Got faulty ws event data with no "
                                               "existing member data!")
                                member = None
                                if not cached_member:
                                    logger.warning("[HOUSE_MEMBER_UPDATE] Unable to find member in the cache! "
                                                   f"USER_ID={data.get('user_id')}")

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_house_member_update(
                                old=cached_member,
                                new=member,
                                house=house
                            ))

                        except Exception as e:
                            logger.exception("[HOUSE_MEMBER_UPDATE] Failed to handle event and trigger "
                                             f"'on_member_update'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_member_update_handler())

            elif swarm_event == "HOUSE_MEMBER_JOIN":
                """
                A user joined a house
                
                Json-Data:
                house_id: string,
                joined_at: timestamp,
                roles: []
                length: int
                user: {
                    id: string,
                    name: string,
                    user_flags: string,
                    username: string,
                }
                """
                # In work
                if self._ready:
                    async def house_join_handler():
                        """

                        """
                        data = response_data

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_join_handler())

            elif swarm_event == "ROOM_CREATE":
                """
                A room was created in a house
                
                Json-Data:
                house_id: string,
                id: string,
                name: string,
                position: int,
                type: int
                """
                # In work
                if self._ready:
                    async def room_create_handler():
                        pass

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(room_create_handler())

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
                if self._ready:
                    async def house_member_exit_handler():
                        """
                        Handler for a house member exit event. Removes the member
                        from the house members list and triggers on_house_exit and
                        returns as parameter the user obj and house obj
                        """
                        try:
                            data = response_data
                            user = utils.get(self._users, id=int(data.get('id')))
                            house = utils.get(self._houses, id=int(data.get('house_id')))
                            if house:
                                cached_mem = utils.get(house._members, user_id=int(data.get('id')))
                                if cached_mem:
                                    house._members.remove(cached_mem)
                                else:
                                    logger.warning("[HOUSE_MEMBER_EXIT] Failed to find member in the client cache! "
                                                   "Possibly faulty client data!")
                            else:
                                logger.warning("[HOUSE_MEMBER_EXIT] Failed to find House in the client cache! "
                                               "Possibly faulty client data!")

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_house_member_exit(
                                user=user,
                                house=house
                            ))

                        except Exception as e:
                            logger.exception("[HOUSE_MEMBER_EXIT] Failed to handle event and trigger "
                                             f"'on_house_exit'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_member_exit_handler())

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
                if self._ready:
                    async def presence_update_handler():
                        """
                        Handler for a User Presence update
                        """
                        try:
                            user = types.User(response_data, self.http)
                            presence = types.Presence(response_data, user, self.http)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_presence_update(presence, user))

                        except Exception as e:
                            logger.exception("[PRESENCE_UPDATE] Failed to handle event and trigger "
                                             f"'on_presence_update'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(presence_update_handler())

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
                    async def msg_create_handler():
                        """
                        Handler for created messages which will trigger the 'on_message_create' event
                        and update cached data (room, author). Will return as parameter the created
                        msg object.
                        """
                        try:
                            data = response_data
                            if data.get('house_id'):
                                house = utils.get(self._houses, id=int(data.get('house_id', 0)))
                            else:
                                house = None

                            if house:
                                # Updating the last message id in the Room
                                room = utils.get(self._rooms, id=int(data.get('room_id', 0)))
                                if room in self._rooms:
                                    self._rooms.remove(room)
                                    room._last_message_id = data.get('id')
                                    self._rooms.append(room)
                                else:
                                    room = None
                                    logger.warning("[MESSAGE_CREATE] Unable to find private-room in the cache! "
                                                   f"ROOM_ID={data.get('room_id')}")

                            else:
                                # Updating the last message id in the Private-Room
                                private_room = utils.get(self._private_rooms, id=int(data.get('room_id', 0)))
                                if private_room:
                                    self._private_rooms.remove(private_room)
                                    private_room._last_message_id = data.get('id')
                                    self._private_rooms.append(private_room)

                                    room = private_room
                                else:
                                    room = None
                                    logger.warning("[MESSAGE_CREATE] Unable to find private-room in the cache! "
                                                   f"ROOM_ID={data.get('room_id')}")

                            # Removing the old user and appending the new data so it's up-to-date
                            cached_author = utils.get(self._users, id=int(data.get('author_id', 0)))
                            if data.get('author') is not None:
                                author = types.User(data['author'], self.http)

                                if cached_author:
                                    # Removing the old data from the list
                                    self._users.remove(cached_author)
                                self._users.append(author)
                            else:
                                logger.warning("[MESSAGE_CREATE] Author from incoming ws event data not found "
                                               "in cache! Possibly faulty client data!")
                                author = None
                                if not cached_author:
                                    logger.warning("[MESSAGE_CREATE] Unable to find author in the cache! "
                                                   f"USER_ID={data.get('author_id')}")

                            msg = types.Message(response_data, self.http, house, room, author)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_message_create(msg))

                        except Exception as e:
                            logger.exception("[MESSAGE_CREATE] Failed to handle event and trigger 'on_message_create'! "
                                             f"Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(msg_create_handler())

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
                if self._ready:
                    async def msg_delete_handler():
                        """
                        Handler for a deleted message which will trigger the on_message_delete event
                        and return as parameter a DeletedMessage object.
                        """
                        try:
                            msg = types.DeletedMessage(response_data)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_message_delete(msg))

                        except Exception as e:
                            logger.exception("[MESSAGE_DELETE] Failed to handle event and trigger 'on_message_delete'! "
                                             f"Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(msg_delete_handler())

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
                    async def msg_update_handler():
                        """
                        Handler for a deleted message which will create a new msg object
                        and return as parameter the object.
                        """
                        try:
                            # Removes old data in the client cache if possible and reuses older data since
                            # no new data is getting sent with the event.

                            data = response_data
                            if data.get('house_id') is not None:
                                house = utils.get(self._houses, id=int(data.get('house_id', 0)))
                            else:
                                house = None

                            if house:
                                # Updating the last message id in the Room
                                room = utils.get(self._rooms, id=int(data.get('room_id', 0)))
                                if room in self._rooms:
                                    self._rooms.remove(room)
                                    room._last_message_id = data.get('id')
                                    self._rooms.append(room)
                                else:
                                    room = None
                                    logger.warning("[MESSAGE_UPDATE] Unable to find private-room in the cache! "
                                                   f"ROOM_ID={data.get('room_id')}")

                            else:
                                # Updating the last message id in the Private-Room
                                private_room = utils.get(self._private_rooms, id=int(data.get('room_id', 0)))
                                if private_room:
                                    self._private_rooms.remove(private_room)
                                    private_room._last_message_id = data.get('id')
                                    self._private_rooms.append(private_room)

                                    room = private_room
                                else:
                                    logger.warning("[MESSAGE_UPDATE] Unable to find private-room in the cache! "
                                                   f"ROOM_ID={data.get('room_id')}")
                                    room = None

                            # Getting the author from the cache if it exists
                            cached_author = utils.get(self._users, id=int(data.get('author_id', 0)))
                            if not cached_author:
                                logger.warning("[MESSAGE_UPDATE] Author from incoming ws event data not found "
                                               "in cache! Possibly faulty client data!")
                                author = None
                            else:
                                # Using the cached author since no data is received
                                author = cached_author

                            message = types.Message(data, self.http, house=house, room=room, author=author)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_message_update(message))

                        except Exception as e:
                            logger.exception("[MESSAGE_UPDATE] Failed to handle event and trigger 'on_message_update'! "
                                             f"Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(msg_update_handler())

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
                if self._ready:
                    async def typing_start_handler():
                        """
                        Handler for the typing_start event that will trigger the event
                        on_typing_start and return as parameter the typing object with
                        the room, house and member as attributes.
                        """
                        try:
                            data = response_data
                            if data.get('recipient_ids') is None:
                                room = utils.get(self._rooms, id=int(response_data.get('room_id', 0)))
                                house = utils.get(self._houses, id=int(response_data.get('house_id', 0)))
                                author = utils.get(house.members, id=int(response_data.get('author_id', 0)))
                            else:
                                room = utils.get(self._private_rooms, id=int(response_data.get('room_id', 0)))
                                house = None
                                author = utils.get(self._users, id=int(response_data.get('author_id', 0)))

                            typing = types.Typing(response_data, author, room, house, self.http)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_typing_start(typing))

                        except Exception as e:
                            logger.exception("[TYPING_START] Failed to handle event and trigger 'on_typing_start'! "
                                             f"Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(typing_start_handler())

            elif swarm_event == "TYPING_END":
                """
                Typing of a user ended
                
                Currently not existing!
                
                Json-Data:
                """
                if self._ready:
                    async def typing_end_handler():
                        """
                        Handler for the typing_end event which will trigger the typing_end
                        event and return as parameter the Typing object with the room,
                        house and member as parameter.

                        Currently non-existed and only serves as placeholder in case
                        it is added in the future
                        """
                        try:
                            room = utils.get(self._rooms, id=int(response_data.get('room_id', 0)))
                            house = utils.get(self._houses, id=int(response_data.get('room_id', 0)))
                            member = utils.get(house.members, id=int(response_data.get('room_id', 0)))
                            typing = types.Typing(response_data, member, room, house, self.http)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_typing_end(typing))

                        except Exception as e:
                            logger.exception("[TYPING_END] Failed to handle event and trigger "
                                             f"'on_typing_end'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(typing_end_handler())

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
                if self._ready:
                    async def member_chunk_handler():
                        """
                        In Work!

                        Handler for a house member chunk update which updates for every
                        sent member object the object in the house list. Triggers
                        on_house_member_chunk and returns as parameter the changed
                        members, the raw data and the house object.
                        """
                        try:
                            data = response_data
                            house = utils.get(self._houses, id=int(data.get('house_id')))

                            mem_dict = data.get('members')
                            members = []
                            for mem_id in mem_dict.keys():
                                cached_mem = utils.get(house.members, id=int(mem_id))
                                if cached_mem is not None:
                                    house._members.remove(cached_mem)
                                    mem = types.Member(mem_dict.get(mem_id), self.http, house)
                                    house._members.append(mem)
                                    members.append(mem)
                                else:
                                    name = mem_dict.get(mem_id).get('name')
                                    logger.warning(f"[HOUSE_MEMBERS_CHUNK] Failed to update member data of "
                                                   f"{name} in house {house.name}")

                                cached_user = utils.get(self._users, id=int(mem_id))
                                if cached_user is not None:
                                    self._users.remove(cached_user)
                                    user = types.User(mem_dict.get(mem_id), self.http)
                                    self._users.append(user)
                                else:
                                    name = mem_dict.get(mem_id).get('name')
                                    logger.warning(f"[HOUSE_MEMBERS_CHUNK] Failed to update user data of "
                                                   f"{name} in client cache!")

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_house_member_chunk(
                                members=members,
                                data=data,
                                house=house))

                        except Exception as e:
                            logger.exception("[HOUSE_MEMBERS_CHUNK] Failed to handle event and trigger "
                                             f"'on_house_member_chunk'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(member_chunk_handler())

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
                if self._ready:
                    async def batch_house_member_handler():
                        """
                        In Work!

                        Handler for a batch house member update that includes a list of
                        members that were updated. Triggers on_batch_house_member_update
                        and returns as parameters the members list, the raw data and the house obj

                        """
                        try:
                            data = response_data
                            house = utils.get(self._houses, id=int(data.get('house_id')))
                            members = list([types.Member(data, house, self.http) for data in data.get('data', [])])

                            for mem in members:
                                mem_id = getattr(mem, "id")
                                # Checking whether the id exists and the object was created correctly
                                if mem_id:
                                    cached_mem = utils.get(house.members, id=int(mem_id))
                                    if cached_mem is not None:
                                        # Replaying the members data
                                        house._members.remove(cached_mem)
                                        house._members.append(mem)
                                    else:
                                        logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update member data "
                                                       f"of {mem.name} in house {house.name}")
                                else:
                                    logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update member data of "
                                                   f"unknown member in house {house.name} because of faulty user data! "
                                                   "Possibly faulty client data!")

                            users = list([types.User(data, self.http) for data in data.get('data', [])])

                            for user in users:
                                usr_id = getattr(user, "id")
                                # Checking whether the id exists and the object was created correctly
                                if usr_id:
                                    cached_user = utils.get(self._users, id=int(usr_id))
                                    if cached_user is not None:
                                        # Replaying the users data
                                        self._users.remove(cached_user)
                                        self._users.append(user)
                                    else:
                                        logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update user data "
                                                       "of {user.name} in house {house.name}! Possibly faulty client data!")
                                else:
                                    logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update user data "
                                                   f"of unknown user in house {house.name} because of faulty user data!"
                                                   " Possibly faulty client data!")

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_batch_house_member_update(
                                members=members,
                                data=data,
                                house=house))

                        except Exception as e:
                            logger.exception("[BATCH_HOUSE_MEMBER_UPDATE] Failed to handle event and trigger "
                                             f"'on_batch_house_member_update'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(batch_house_member_handler())

            elif swarm_event == "HOUSE_ENTITIES_UPDATE":
                """
                House entities was updated
                
                Json-Data:
                op: 0
                d: {
                  house_id: string,
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
                if self._ready:
                    async def house_entity_update_handler():
                        """
                        In Work!

                        Handler for a house entity update. Triggers on_house_entity_update and
                        returns as parameter the house obj, the entity obj and the raw data
                        """
                        try:
                            data = response_data
                            house = utils.get(self._houses, id=int(data.get('house_id')))
                            entity = None  # TODO! Insert entity

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_house_entity_update(
                                house=house,
                                entity=entity,
                                data=data
                            ))

                        except Exception as e:
                            logger.exception("[HOUSE_ENTITIES_UPDATE] Failed to handle event and trigger "
                                             f"'on_house_entity_update'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(house_entity_update_handler())

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
                if self._ready:
                    async def relationship_update_handler():
                        """
                        Handler for a relationship update. Triggers on_relationship_update
                        and returns as parameter the relationship obj.
                        """
                        try:
                            data = response_data

                            cache_relationship = utils.get(self._relationships, id=int(data.get('id')))
                            relationship = types.Relationship(data, self.http)
                            if cache_relationship:
                                # Removing the old data
                                self._relationships.remove(cache_relationship)

                            # Adding the new data
                            self._relationships.append(relationship)

                            # Creating a new task for handling the event
                            # TODO! Needs error handling and name traceback and log!
                            asyncio.create_task(self._event_handler.ev_relationship_update(
                                relationship=relationship
                            ))

                        except Exception as e:
                            logger.exception("[RELATIONSHIP_UPDATE] Failed to handle event and trigger "
                                             f"'on_relationship_update'! Exception: {e}")

                    # => Creating a parallel task to not slow down event handler
                    asyncio.create_task(relationship_update_handler())
            else:
                logger.error(f"[WEBSOCKET] << Unknown Event {swarm_event} without Handler!")

        except Exception as e:
            logger.debug(f"[WEBSOCKET] << Failed to handle Event in the websocket! "
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return
