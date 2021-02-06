import asyncio
import time
import sys
import os
import json
import logging
import typing
import aiohttp

__all__ = ['Websocket']

import openhivenpy.types as types
from ..exceptions import exception as errs
from ..utils import utils as utils
from ..events import EventHandler
from ..settings import load_env

logger = logging.getLogger(__name__)

# Loading the environment variables
load_env()
# Setting the default values to the currently set defaults in the openhivenpy.env file
_default_host = os.getenv("HIVEN_HOST")
_default_api_version = os.getenv("HIVEN_API_VERSION")
_default_connection_heartbeat = int(os.getenv("CONNECTION_HEARTBEAT"))
_default_close_timeout = int(os.getenv("CLOSE_TIMEOUT"))


class Websocket(types.Client):
    """
    Websocket Class that will listen to the Hiven Swarm and handle server-sent message and trigger events if received!
    Uses an instance of `openhivenpy.EventHandler` for EventHandling and will execute registered functions.
    """

    def __init__(
            self,
            token: str,
            *,
            restart: bool = False,
            log_ws_output: bool = False,
            host: str = _default_host,
            api_version: str = _default_api_version,
            heartbeat: int = _default_connection_heartbeat,
            close_timeout: int = _default_close_timeout,
            event_handler: EventHandler,
            event_loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
            **kwargs):
        """
        Object Instance Construction
        :param token: Authorisation Token for Hiven
        :param restart: If set to True the process will restart if an exception occurred
        :param host: Url for the API which will be used to interact with Hiven.
                     Defaults to the pre-set environment host (api.hiven.io)
        :param api_version: Version string for the API Version. Defaults to the pre-set environment version (v1)
        :param heartbeat: Intervals in which the bot will send heartbeats to the Websocket.
                          Defaults to the pre-set environment heartbeat (30000)
        :param close_timeout: Seconds after the websocket will timeout after the end handshake didn't complete
                              successfully. Defaults to the pre-set environment close_timeout (40)
        :param event_loop: Event loop that will be used to execute all async functions. Will use 'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was created yet
        :param event_handler: Handler for Websocket Events
        """

        self._host = host
        self._api_version = api_version

        self._WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self._ENCODING = "json"

        # In milliseconds
        self._HEARTBEAT = heartbeat
        self._TOKEN = token
        self._close_timeout = close_timeout
        self._event_handler = event_handler
        self._event_loop = event_loop
        self._restart = restart
        self._log_ws_output = log_ws_output
        self._CUSTOM_HEARTBEAT = False if self._HEARTBEAT == int(os.getenv("CONNECTION_HEARTBEAT")) else True
        self._ws_session = None
        self._ws = None
        self._connection_task = None
        self._lifesignal = None

        # Websocket and Connection Attribute
        self._open = False
        self._connection_start = None
        self._startup_time = None
        self._initialised = False
        self._ready = False
        self._connection_start = None
        self._connection_status = "CLOSED"

        # Initialising the parent class Client which handles the data
        super().__init__()

    @property
    def open(self):
        return getattr(self, '_open', False)

    @property
    def closed(self):
        return not getattr(self, 'open', False)

    @property
    def close_timeout(self) -> int:
        return getattr(self, '_close_timeout', None)

    @property
    def websocket_url(self) -> str:
        return getattr(self, '_WEBSOCKET_URL', None)

    @property
    def encoding(self) -> str:
        return getattr(self, '_ENCODING', None)

    @property
    def heartbeat(self) -> int:
        return getattr(self, '_HEARTBEAT', None)

    @property
    def ws_session(self) -> aiohttp.ClientSession:
        return getattr(self, '_ws_session', None)

    @property
    def ws(self) -> aiohttp.ClientWebSocketResponse:
        return getattr(self, '_ws', None)

    @property
    def ws_connection(self) -> asyncio.Task:
        return getattr(self, '_connection', None)

    @property
    def connection_status(self) -> str:
        return getattr(self, '_connection_status', 'CLOSED')

    @property
    def event_handler(self) -> EventHandler:
        return getattr(self, '_event_handler', None)

    @property
    def ready(self) -> bool:
        return getattr(self, '_ready', False)

    @property
    def initialised(self) -> bool:
        return getattr(self, '_initialised', False)

    # Starts the connection over a new websocket
    async def ws_connect(self, session: aiohttp.ClientSession, heartbeat: int = None) -> None:
        """
        Creates a connection to the Hiven API.

        Not Intended for User Usage
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

                    # Waits until the Connection Start event has finished
                    await self.event_handler.dispatch_on_connection_start()

                    # Running the lifesignal and response handling parallel
                    await asyncio.gather(self.lifesignal(ws), self.message_handler(ws=ws))

            except KeyboardInterrupt:
                pass

            except Exception as ws_e:
                utils.log_traceback(level='critical',
                                    msg="[WEBSOCKET] Traceback:",
                                    suffix=f"[WEBSOCKET] The connection to Hiven failed to be kept alive or started;\n"
                                           f"{sys.exc_info()[0].__name__}, {str(ws_e)}")

                # Closing
                close = getattr(self, "close", None)
                if callable(close):
                    await close(close_exec_loop=not self._restart,
                                reason="WebSocket encountered an error!",
                                block_restart=not self._restart)

                return

            finally:
                self._open = False
                return

        # Creating a task that wraps the coroutine
        self._connection_task = asyncio.create_task(ws_connection(), name="openhivenpy-ws-connection")

        # Running the task in the background
        try:
            await self._connection_task
        except KeyboardInterrupt:
            pass

        # Avoids that the user notices that the task was cancelled!
        except asyncio.CancelledError:
            logger.debug("[WEBSOCKET] << The websocket Connection to Hiven unexpectedly stopped and was cancelled! "
                         "Likely caused due to an error or automatic/forced closing!")

        except Exception as e:
            logger.debug("[WEBSOCKET] << The websocket Connection to Hiven unexpectedly stopped and failed to process! "
                         f"> {sys.exc_info()[0].__name__}: {e}!")

            raise errs.GatewayException(f"[WEBSOCKET] << Exception in main-websocket process!"
                                        f"> {sys.exc_info()[0].__name__}: {e}!")

    # Loop for receiving messages from Hiven
    async def message_handler(self, ws) -> None:
        """
        Message Handler for the websocket that will handle messages received over the websocket connection
        and if needed trigger an event using the function text_based_message_handler(), which triggers events
        if needed. The incoming messages in this case are handled when they arrive meaning that a loop will
        await a new message and if one is received handle the message and pass it as a dict to the
        text_based_message_handler() if the type is correct json. If it's not it will log a warning containing
        that message!

        :param ws: The aiohttp websocket instance needed for interaction with Hiven
        :return: None - Only returns if the process failed or the websocket was forced to close!
        """
        # This process will break if a close frame was received, which automatically
        # closes the connection. This is then only way the connection should normally close
        # except a user forced the ws to close or a exception was raised while processing.
        while self.open:
            ws_msg = await ws.receive()
            if ws_msg is not None:
                # Logging the Received Type
                logger.debug(f"[WEBSOCKET] << Got Type {ws_msg.type} - {repr(ws_msg.type)}")

                # Checking if the msg type is text and therefore can be used
                if ws_msg.type == aiohttp.WSMsgType.TEXT:
                    if ws_msg.data is not None:
                        try:
                            json_data = json.loads(ws_msg.data)
                        except ValueError:
                            json_data = None
                    else:
                        json_data = None

                    # If the data is in json format it can be handled as event
                    if json_data is not None:
                        # If the op-code is 1 the server expects the client to authorise
                        if json_data.get('op') == 1:
                            # Authorizing with token
                            logger.info("[WEBSOCKET] >> Authorizing with token")
                            json_auth = str(json.dumps({"op": 2, "d": {"token": str(self._TOKEN)}}))
                            await ws.send_str(json_auth)

                            if self._CUSTOM_HEARTBEAT is False:
                                self._HEARTBEAT = json_data['d']['hbt_int']
                                ws.heartbeat = self._HEARTBEAT

                            logger.debug(f"[WEBSOCKET] >> Heartbeat set to {ws.heartbeat}")
                            logger.info("[WEBSOCKET] << Connection to Hiven Swarm established")

                        else:
                            if self._log_ws_output:
                                logger.debug(f"[WEBSOCKET] << Received: {str(json_data)}")

                            if json_data.get('e') == "INIT_STATE":
                                # Initialising the data of the Client
                                await super().initialise_hiven_client_data(json_data.get('d'))

                                # init_time = Time it took to initialise
                                init_time = time.time() - self._connection_start
                                self._initialised = True

                                # Calling the event 'on_init()'
                                await self.event_handler.dispatch_on_init(time=init_time)

                            else:
                                # Calling the websocket message handler for handling the incoming ws message
                                await self.text_based_message_handler(json_data)
                    else:
                        logger.warning(f"[WEBSOCKET] Received unexpected non-json text type: '{ws_msg.data}'")

                elif ws_msg.type == aiohttp.WSMsgType.CLOSE:
                    # Close Frame can be received because of these issues:
                    # - Faulty token
                    # - Error occurred while handling a ws message => aiohttp automatically stops
                    # - Server unreachable
                    # - Hiven send one back because faulty authorisation!
                    logger.debug(f"[WEBSOCKET] << Received close frame with msg='{ws_msg.extra}'!")
                    break

                elif ws_msg.type == aiohttp.WSMsgType.ERROR:
                    logger.critical(f"[WEBSOCKET] Failed to handle response >> {ws.exception()} >>{ws_msg}")
                    raise errs.WSFailedToHandle(ws_msg.data)

        # Closing the websocket instance if it wasn't closed
        if not ws.closed:
            await ws.close()

        logger.info(f"[WEBSOCKET] << Connection to Remote ({self._WEBSOCKET_URL}) closed!")
        self._open = False

        # Trying to fetch the close method of the Connection class which stops the currently running processes
        close = getattr(self, "close", None)
        if callable(close):
            await close(close_exec_loop=True, reason="Response Handler stopped!", block_restart=not self._restart)

        return

    async def lifesignal(self, ws) -> None:
        """
        Lifesignal Task sending lifesignal messages to the Hiven Swarm

        Not Intended for User Usage

        :param ws: The aiohttp websocket instance needed for interaction with Hiven
        :return: None - Only returns if the process failed or the websocket was forced to close!
        """
        try:
            # Life Signal that sends an op-code to Hiven to signalise the client instance is still alive!
            # Will automatically break if the connection status is CLOSING or CLOSED
            async def _lifesignal():
                while self._open and self.connection_status not in ["CLOSING", "CLOSED"]:
                    await asyncio.sleep(self._HEARTBEAT / 1000)  # Converting the Heartbeat to seconds from ms

                    logger.debug(f"[WEBSOCKET] >> Lifesignal at {time.time()}")
                    await ws.send_str(str(json.dumps({"op": 3})))
                return

            self._connection_status = "OPEN"

            # Wrapping the lifesignal into a task so it can be easily stopped if needed
            self._lifesignal = asyncio.create_task(_lifesignal())
            await self._lifesignal
            return

        # If the task is cancelled it will return without logging
        except asyncio.CancelledError:
            return

        except Exception as e:
            utils.log_traceback(level='critical', msg="[WEBSOCKET] Traceback:")
            logger.critical(f"[WEBSOCKET] << Failed to keep lifesignal alive! "
                            f"> {sys.exc_info()[0].__name__}: {e}")

    async def wait_for_ready(self):
        """
        Returns when the WebSocket is ready. Will be used to make sure events that happen while initialisation
        wait until the Client has loaded successfully.

        :return: None when the Websocket is ready
        """
        while True:
            if self.ready:
                return
            await asyncio.sleep(0.05)

    async def wait_for_initialised(self):
        """
        Returns when the WebSocket is initialised. Will be used to make sure events that happen while initialisation
        wait until the Client has initialised successfully.

        :return: None when the Websocket is initialised
        """
        while True:
            if self.initialised:
                return
            await asyncio.sleep(0.05)

    # Event Triggers
    async def text_based_message_handler(self, resp_data: dict):
        """
        Handler for the Websocket events and the message data.

        Triggers based on the passed data an event

        :param resp_data: The incoming WebSocket message
        """
        try:
            ws_msg_data = resp_data.get('d', {})
            swarm_event = resp_data.get('e', "")

            logger.debug(f"Received Event {swarm_event}")

            if swarm_event == "HOUSE_JOIN":
                event_handler = self.house_join_handler(ws_msg_data)

            elif swarm_event == "HOUSE_LEAVE":
                event_handler = self.house_leave_handler(ws_msg_data)

            elif swarm_event == "HOUSE_DOWN":
                event_handler = self.house_down_handler(ws_msg_data)

            elif swarm_event == "HOUSE_MEMBERS_CHUNK":
                event_handler = self.member_chunk_handler(ws_msg_data)

            elif swarm_event == "HOUSE_MEMBER_JOIN":
                event_handler = self.house_member_join_handler(ws_msg_data)

            elif swarm_event == "HOUSE_MEMBER_ENTER":
                event_handler = self.house_member_enter(ws_msg_data)

            elif swarm_event == "HOUSE_MEMBER_LEAVE":
                event_handler = self.house_member_leave(ws_msg_data)

            elif swarm_event == "HOUSE_MEMBER_EXIT":
                event_handler = self.house_member_exit_handler(ws_msg_data)

            elif swarm_event == "HOUSE_MEMBER_UPDATE":
                event_handler = self.house_member_update_handler(ws_msg_data)

            elif swarm_event == "ROOM_CREATE":
                event_handler = self.room_create_handler(ws_msg_data)

            elif swarm_event == "PRESENCE_UPDATE":
                event_handler = self.presence_update_handler(ws_msg_data)

            elif swarm_event == "MESSAGE_CREATE":
                event_handler = self.message_create_handler(ws_msg_data)

            elif swarm_event == "MESSAGE_DELETE":
                event_handler = self.message_delete_handler(ws_msg_data)

            elif swarm_event == "MESSAGE_UPDATE":
                event_handler = self.message_update_handler(ws_msg_data)

            elif swarm_event == "TYPING_START":
                event_handler = self.typing_start_handler(ws_msg_data)

            elif swarm_event == "BATCH_HOUSE_MEMBER_UPDATE":
                event_handler = self.batch_house_member_handler(ws_msg_data)

            elif swarm_event == "HOUSE_ENTITIES_UPDATE":
                event_handler = self.house_entity_update_handler(ws_msg_data)

            elif swarm_event == "RELATIONSHIP_UPDATE":
                event_handler = self.relationship_update_handler(ws_msg_data)
            else:
                logger.error(f"[WEBSOCKET] << Unknown Event {swarm_event} without Handler!")
                return

            asyncio.create_task(event_handler)

        except Exception as e:
            utils.log_traceback(level='debug',
                                msg="[WEBSOCKET] Traceback:",
                                suffix=f"Failed to handle incoming json-type text message in the websocket; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_down_handler(self, ws_msg_data: dict):
        """
        Handler for downtime of a house! Triggers on_house_down and
        returns as parameter the time of downtime and the house

        If the property unavailable of the message is false

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.initialised:
                data = ws_msg_data

                house = utils.get(self._houses, id=int(data.get('house_id')))
                if data.get('unavailable') is True:
                    logger.debug(f"[HOUSE_DOWN] << Downtime of '{house.name}' reported! "
                                 "House was either deleted or is currently unavailable!")
                    await self.event_handler.dispatch_on_house_down_time(house_id=house.id)
                else:
                    # Removing the deleted house
                    self._houses.remove(house)
                    await self.event_handler.dispatch_on_house_delete(house_id=house.id)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_DOWN] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"> {sys.exc_info()[0].__name__}: {e}")

    async def member_chunk_handler(self, ws_msg_data: dict):
        """
        In Work!

        Handler for a house member chunk update which updates for every
        sent member object the object in the house list. Triggers
        on_house_member_chunk and returns as parameter the changed
        members, the raw data and the house object.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data
                # Fetching the house based on the ID
                house = utils.get(self._houses, id=int(data.get('house_id')))

                # Member data that was sent with the request
                sent_member_data = data.get('members')
                updated_members = []

                # For every member that was sent and their data the stored cached data will be replaced
                for mem_id, mem_data in sent_member_data.items():
                    cached_mem = utils.get(house.members, id=int(mem_id))
                    if cached_mem is not None:
                        # Removing the older cached member
                        house._members.remove(cached_mem)

                        # Creating a new Member Class and appending the new data
                        member = types.Member(mem_data, house, self.http)

                        # Appending the new member
                        house._members.append(member)
                        # Appending to the 'changelog' list the member
                        updated_members.append(member)

                    else:
                        name = sent_member_data.get(mem_id).get('name')
                        logger.warning(f"[HOUSE_MEMBERS_CHUNK] Failed to update member data of "
                                       f"{name} in house {house.name} > Member not found locally!")

                    cached_user = utils.get(self._users, id=int(mem_id))
                    if cached_user is not None:
                        # Removing the older cached user
                        self._users.remove(cached_user)

                        user = types.User(sent_member_data.get(mem_id), self.http)
                        self._users.append(user)
                    else:
                        name = sent_member_data.get(mem_id).get('name')
                        logger.warning(f"[HOUSE_MEMBERS_CHUNK] Failed to update user data of "
                                       f"{name} in client cache! > Member not found locally!")

                await self.event_handler.dispatch_on_house_member_chunk(
                    members=updated_members,
                    data=data,
                    house=house)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_MEMBERS_CHUNK] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_member_enter(self, ws_msg_data: dict):
        """
        Handler for a member going online in a mutual house. Trigger on_house_enter
        and returns as parameters the member obj and house obj.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self._initialised:
                house_id = ws_msg_data.get('house_id')
                if house_id is None:
                    house_id = ws_msg_data.get('house', {}).get('id')

                # Fetching the house
                house = utils.get(self._houses, id=int(house_id))

                # Fetching the cached_member
                cached_member = utils.get(house.members, user_id=int(ws_msg_data.get('user_id', 0)))

                await self.event_handler.dispatch_on_house_member_enter(member=cached_member, house=house)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_MEMBER_ENTER] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_member_update_handler(self, ws_msg_data: dict):
        """
        Handler for a house member update which will trigger on_member_update and return
        as parameter the old member obj, the new member obj and the house.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.initialised:
                data = ws_msg_data
                house = utils.get(self.houses, id=int(data.get('house_id')))

                if house is None:
                    await asyncio.wait_for(self.ready)

                cached_user = utils.get(self._users, id=int(data.get('user_id')))
                user = types.User(data['user'], self.http)

                # Removing the old user
                if cached_user:
                    self._users.remove(cached_user)
                # Appending the new user
                self._users.append(user)

                # Getting the cached member in the house if it exists
                cached_member = utils.get(house.members, user_id=int(data.get('user_id')))
                member = types.Member(data, house, self.http)

                if cached_member:
                    # Removing the old member
                    house._members.remove(cached_member)
                # Appending the new member
                house._members.append(member)

                await self.event_handler.dispatch_on_member_update(old=cached_member, new=member, house=house)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_MEMBER_UPDATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_member_join_handler(self, ws_msg_data: dict):
        """
        Handler for a House Join Event where a user joined a house. Triggers on_member_join and passes the house and
        the member as arguments.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data

                # Fetching the ID of the house
                house_id = data.get('house_id')
                # Fetching the house from the cache
                house = utils.get(self.houses, id=int(house_id))

                user_id = int(data.get('user', {}).get('id'))

                # Fetching the user from the cache
                cached_user = utils.get(self.users, id=user_id)

                if cached_user is None:
                    # Requesting full data of the user
                    raw_data = self.http.request(f"/users/{user_id}")

                    if raw_data:
                        user = types.User(raw_data.get('data'), self.http)
                        # Appending the newly created user-object
                        self._users.append(user)

                    else:
                        raise errs.HTTPReceivedNoData()

                cached_member = utils.get(house.members, user_id=user_id)
                if cached_member is None:
                    # Removing the cached_data
                    house._members.remove(cached_member)

                    member = types.Member(data, house, self.http)
                    # Appending the newly created member-object
                    house._members.append(member)

                await self.event_handler.dispatch_on_house_member_join(member=cached_member, house=house)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_MEMBER_JOIN] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def room_create_handler(self, ws_msg_data: dict):
        """
        Handler for Room creation in a house. Triggers on_room_create() and passes the room as argument

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data

                # House Room
                if data.get('house_id'):
                    house = utils.get(self._houses, id=int(data.get('house_id')))

                    # Creating a new room
                    room = types.Room(data, self.http, house)
                    self._rooms.append(room)

                    # Appending the updated room
                    house._rooms.append(room)
                else:
                    # Private Group Room
                    room = types.PrivateGroupRoom(data, self.http)
                    self._private_rooms.append(room)

                await self.event_handler.dispatch_on_room_create(room=room)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[ROOM_CREATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_member_exit_handler(self, ws_msg_data: dict):
        """
        Handler for a house member exit event. Removes the member
        from the house members list and triggers on_house_exit and
        returns as parameter the user obj and house obj.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data
                house = utils.get(self._houses, id=int(data.get('house_id')))
                cached_mem = utils.get(house.members, user_id=int(data.get('id')))

                await self.event_handler.dispatch_on_house_member_exit(member=cached_mem, house=house)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_MEMBER_EXIT] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def presence_update_handler(self, ws_msg_data: dict):
        """
        Handler for a User Presence update

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                user = types.User(ws_msg_data, self.http)
                presence = types.Presence(ws_msg_data, user, self.http)

                # TODO! Update user presence!

                await self.event_handler.dispatch_on_presence_update(presence, user)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[PRESENCE_UPDATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def message_create_handler(self, ws_msg_data: dict):
        """
        Handler for a user-created messages which will trigger the 'on_message_create' event.
        Will return as parameter the created msg object.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data
                if data.get('house_id'):
                    house = utils.get(self._houses, id=int(data.get('house_id', 0)))
                else:
                    house = None

                if house:
                    # Updating the last message ID in the Room
                    room = utils.get(self._rooms, id=int(data.get('room_id', 0)))
                    if room is not None:
                        # Updating the last message_id
                        room._last_message_id = data.get('id')
                    else:
                        logger.warning("[MESSAGE_CREATE] Unable to find room in the cache! "
                                       f"ROOM_ID={data.get('room_id')}")

                # It's a private_room with no existing house
                else:
                    # Updating the last message ID in the Private-Room
                    private_room = utils.get(self._private_rooms, id=int(data.get('room_id', 0)))
                    if private_room is not None:
                        # Updating the last message_id
                        private_room._last_message_id = data.get('id')

                        # Room where the message was sent => private_room
                        room = private_room
                    else:
                        room = None
                        logger.warning("[MESSAGE_CREATE] Unable to find private-room in the cache! "
                                       f"ROOM_ID={data.get('room_id')}")

                author = utils.get(self._users, id=int(data.get('author_id')))
                msg = types.Message(ws_msg_data, self.http, house, room, author)

                await self.event_handler.dispatch_on_message_create(msg)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[MESSAGE_CREATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def message_delete_handler(self, ws_msg_data: dict):
        """
        Handler for a deleted message which will trigger the on_message_delete event
        and return as parameter a DeletedMessage object.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                msg = types.DeletedMessage(ws_msg_data)

                # Creating a new task for handling the event
                # TODO! Needs error handling and name traceback and log!
                await self.event_handler.dispatch_on_message_delete(msg)
            else:
                return
        except Exception as e:
            utils.log_traceback(msg="[MESSAGE_DELETE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"> {sys.exc_info()[0].__name__}: {e}")

    async def message_update_handler(self, ws_msg_data: dict):
        """
        Handler for a deleted message which will create a new msg object
        and return as parameter the object.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                # Removes old data in the client cache if possible and reuses older data since
                # no new data is getting sent with the event.

                data = ws_msg_data
                if data.get('house_id') is not None:
                    house = utils.get(self._houses, id=int(data.get('house_id', 0)))
                else:
                    house = None

                if house:
                    # Updating the last message ID in the Room
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
                    # Updating the last message ID in the Private-Room
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

                await self.event_handler.dispatch_on_message_update(message)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[MESSAGE_UPDATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def relationship_update_handler(self, ws_msg_data: dict):
        """
        Handler for a relationship update. Triggers on_relationship_update
        and returns as parameter the relationship obj.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data

                cache_relationship = utils.get(self._relationships, id=int(data.get('id')))
                relationship = types.Relationship(data, self.http)
                if cache_relationship:
                    # Removing the old data
                    self._relationships.remove(cache_relationship)

                # Adding the new data
                self._relationships.append(relationship)

                await self.event_handler.dispatch_on_relationship_update(relationship=relationship)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[RELATIONSHIP_UPDATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_join_handler(self, ws_msg_data: dict):
        """
        Handler for the dispatch_on_house_add event of the connected client which will trigger
        the on_house_join event and return as parameter the house.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self._initialised:
                data = ws_msg_data

                # Creating a house object that will then be appended
                house = await types.House.from_dict(data, self.http, client_id=self.id)

                for member_data in data['members']:
                    if hasattr(member_data, 'id'):
                        user_id = int(member_data.get('id'))
                    else:
                        # Falling back to the nested user object and the ID that is stored there
                        user_id = int(member_data['user'].get('id', 0))

                    # Getting the user from the list if it exists
                    cached_user = utils.get(self._users, id=user_id)

                    # If it doesn't exist it needs to be added to the list
                    if cached_user is None:
                        # Appending the new user
                        self._users.append(types.User(member_data, self.http))

                for room in ws_msg_data['rooms']:
                    self._rooms.append(types.Room(room, self.http, house))

                # Appending to the client houses list
                self._houses.append(house)

                await self.event_handler.dispatch_on_house_add(house)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_JOIN] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_leave_handler(self, ws_msg_data: dict):
        """
        Handler for the event on_house_remove, which will return as parameter the removed house.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self._initialised:
                house = utils.get(self._houses, id=int(ws_msg_data.get('house_id')))

                if house:
                    # Removing the house
                    self._houses.remove(house)
                else:
                    logger.debug("[HOUSE_LEAVE] Unable to locate left house in house cache! "
                                 "Possibly faulty Client data!")

                await self.event_handler.dispatch_on_house_remove(house=house)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_LEAVE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_entity_update_handler(self, ws_msg_data: dict):
        """
        Handler for a house entity update. Triggers on_house_entity_update and
        returns as parameter the house obj, the entity obj and the raw data

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data
                house = utils.get(self._houses, id=int(data.get('house_id')))
                entity = types.Entity(data, self.http)

                await self.event_handler.dispatch_on_house_entity_update(house=house, entity=entity, data=data)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_ENTITIES_UPDATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def batch_house_member_handler(self, ws_msg_data: dict):
        """
        In Work!

        Handler for a batch house member update that includes a list of
        members that were updated. Triggers on_batch_house_member_update
        and returns as parameters the members list, the raw data and the house obj

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:

                data = ws_msg_data
                house = utils.get(self._houses, id=int(data.get('house_id')))

                # Creating a list of all updated members
                members = list([types.Member(data, house, self.http) for data in data.get('data')])

                # For every created member the local member data will be replaced
                for member in members:
                    mem_id = getattr(member, "id")

                    # Checking whether the ID exists and the object was created correctly
                    if mem_id:
                        cached_mem = utils.get(house.members, id=int(mem_id))
                        if cached_mem is not None:
                            # Replacing the cached member with the newly created member object
                            house._members.remove(cached_mem)
                            house._members.append(member)
                        else:
                            logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update member data "
                                           f"of {member.name} in house {house.name}")
                    else:
                        logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update member data of "
                                       f"unknown member in house {house.name} because of faulty user data! "
                                       "Possibly faulty client data!")

                # Creating a list of all updated users
                users = list([types.User(data, self.http) for data in data.get('data')])

                # For every created user the local user data will be replaced
                for user in users:
                    usr_id = getattr(user, "id")
                    # Checking whether the ID exists and the object was created correctly
                    if usr_id:
                        cached_user = utils.get(self._users, id=int(usr_id))
                        if cached_user is not None:
                            # Replacing the cached user with the newly created user object
                            self._users.remove(cached_user)
                            self._users.append(user)
                        else:
                            logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update user data "
                                           "of {user.name} in house {house.name}! Possibly faulty client data!")
                    else:
                        logger.warning(f"[BATCH_HOUSE_MEMBER_UPDATE] Failed to update user data "
                                       f"of unknown user in house {house.name} because of faulty user data!"
                                       " Possibly faulty client data!")

                await self.event_handler.dispatch_on_batch_house_member_update(members=members, data=data, house=house)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[BATCH_HOUSE_MEMBER_UPDATE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def typing_start_handler(self, ws_msg_data: dict):
        """
        Handler for the typing_start event that will trigger the event
        on_typing_start and return as parameter the typing object with
        the room, house and member as attributes.

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self.ready:
                data = ws_msg_data

                # recipient_ids only exists in private room typing so it is a house if it does not exist!
                if data.get('recipient_ids') is None:
                    room = utils.get(self._rooms, id=int(data.get('room_id')))
                    house = utils.get(self._houses, id=int(data.get('house_id')))
                    author = utils.get(house.members, id=int(data.get('author_id')))
                else:
                    room = utils.get(self._private_rooms, id=int(data.get('room_id')))
                    house = None
                    author = utils.get(self._users, id=int(data.get('author_id')))

                typing = types.UserTyping(data, author, room, house, self.http)

                await self.event_handler.dispatch_on_typing_start(typing)

            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[TYPING_START] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")

    async def house_member_leave(self, ws_msg_data):
        """
        Event for a member leaving a house. Triggers on_house_member_leave()

        :param ws_msg_data: The incoming ws text msg - Should be in correct python dict format
        """
        try:
            if self._initialised:
                data = ws_msg_data
                house = utils.get(self._houses, id=int(data.get('house_id')))
                cached_mem = utils.get(house.members, user_id=int(data.get('id')))

                # Removing the cached member
                house._members.remove(cached_mem)

                await self.event_handler.dispatch_on_house_member_leave(member=cached_mem, house=house)
            else:
                return

        except Exception as e:
            utils.log_traceback(msg="[HOUSE_MEMBER_LEAVE] Traceback:",
                                suffix="Failed to handle the event due to an exception occurring; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
