import asyncio
import json
import logging
import os
import typing
import time
import aiohttp
from enum import IntEnum
from yarl import URL

from ..exception import RestartSessionError, SessionCreateError
from .messagebroker import MessageBroker

__all__ = ['HivenWebSocket']

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = os.getenv("WS_ENDPOINT")


class KeepAlive:
    def __init__(self, ws):
        self.ws = ws
        self._heartbeat = ws.heartbeat
        self._task = None
        self._active = False

    async def run(self):
        """ Runs the current KeepAlive process in a loop that can be cancelled using `KeepAlive.stop()` """
        self._active = True
        while self.ws.open and self._active:
            try:
                self._task = asyncio.create_task(asyncio.wait_for(self.ws.send_heartbeat(), 30))
                await asyncio.sleep(self._heartbeat / 1000)
            except asyncio.CancelledError:
                return
            except Exception:
                raise

    async def stop(self):
        """ Stops the running KeepAlive loop """
        if self._task.cancelled():
            self._task.cancel()
        self._active = False
        self._task = None


class HivenWebSocket:
    def __init__(self,
                 socket,
                 *,
                 loop: asyncio.AbstractEventLoop,
                 heartbeat: int,
                 close_timeout: int,
                 log_ws_output: bool = False):
        self.socket = socket
        self.loop = loop
        self.parsers = None
        self.client = None
        self._open = False
        self._ready = False
        self.log_ws_output = log_ws_output

        # Close code used to represent the status of the aiohttp websocket after it closed
        self._close_code = None
        self._startup_time = None
        self._connection_start = None
        self._connection_status = "CLOSED"
        self._token = None
        self._heartbeat = heartbeat
        self._close_timeout = close_timeout

        self.message_broker = MessageBroker()
        self.keep_alive = KeepAlive(self)

    @classmethod
    async def create_from_client(cls,
                                 client,
                                 close_timeout: int,
                                 heartbeat: int,
                                 loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                                 **kwargs):
        endpoint = URL(DEFAULT_ENDPOINT)

        socket = await client.http.session.ws_connect(
            endpoint.human_repr(), timeout=close_timeout, heartbeat=heartbeat, max_msg_size=0
        )
        ws = cls(socket, loop=loop, heartbeat=heartbeat, close_timeout=close_timeout, **kwargs)
        ws._connection_start = time.time()
        ws.client = client
        ws.parsers = client.parsers
        ws._token = client.token
        ws._open = True

        return ws

    class OPCode(IntEnum):
        EVENT = 0
        CONNECTION_START = 1
        AUTH = 2
        HEARTBEAT = 3

    @property
    def token(self) -> str:
        return getattr(self, '_token', None)

    @property
    def startup_time(self) -> int:
        return getattr(self, '_startup_time', None)

    @property
    def connection_start(self) -> int:
        return getattr(self, '_connection_start', None)

    @property
    def open(self) -> bool:
        return getattr(self, '_open', None)

    @property
    def ready(self) -> bool:
        return getattr(self, '_ready', None)

    @property
    def heartbeat(self) -> bool:
        return getattr(self, '_heartbeat', None)

    @property
    def close_timeout(self) -> bool:
        return getattr(self, '_close_timeout', None)

    async def send_heartbeat(self):
        """ Sends a heartbeat with the additional op-code for keeping the connection alive"""
        try:
            await self.socket.send_str(str(json.dumps({
                "op": self.OPCode.HEARTBEAT
            })))
        except Exception as e:
            raise RestartSessionError("Failed to send heartbeat to WebSocket host!")

    async def send_auth(self):
        """ Sends the authentication header to the Hiven Endpoint"""
        try:
            auth = str(json.dumps({
                "op": self.OPCode.AUTH,
                "d": {
                    "token": self.token
                }
            }))
            await self.socket.send_str(auth)
        except Exception as e:
            raise SessionCreateError(f"Failed to send auth to the host due to exception: {e}")

    async def listening_loop(self):
        """ Listens infinitely for WebSocket Messages and will trigger events accordingly """
        while True:
            await self.wait_for_event()

    async def wait_for_event(self, handler: typing.Callable = None):
        """
        Waits for an event or websocket message and then triggers appropriately the events or raises Exceptions

        :param handler: Handler Awaitable that will be executed instead of `received_message()` if not None
        """
        msg = await self.socket.receive()

        logger.debug(f"[WEBSOCKET] Received WebSocket Message Type '{msg.type.name}'")

        if msg.type == aiohttp.WSMsgType.TEXT:
            return await self.received_message(msg) if handler is None else await handler(msg)

        elif msg.type == aiohttp.WSMsgType.BINARY:
            if type(msg) is bytes:
                msg = msg.data.decode("utf-8")
            else:
                return
            return await self.received_message(msg) if handler is None else await handler(msg)

        elif msg.type == aiohttp.WSMsgType.CLOSE or msg.type == aiohttp.WSMsgType.CLOSING:
            logger.error("[WEBSOCKET] Encountered an Exception in the Websocket! WebSocket will force restart!")
            raise RestartSessionError()

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(
                f"[WEBSOCKET] Encountered an Exception in the Websocket! WebSocket will force restart! {msg.extra}"
            )
            raise RestartSessionError()

    async def received_init_event(self, msg) -> typing.Tuple:
        """ Only intended for the purpose of initialising the Client! Will be called by `received_init` on startup """
        _msg = msg.json()
        op, event, d = self._extract_event(_msg)

        if op == self.OPCode.EVENT:
            return event, d, _msg
        else:
            logger.warning(f"[WEBSOCKET] Received unknown websocket op-code message: {op}: {msg}")
            return None, None, None

    async def received_init(self, msg: dict, client):
        """
        Receives the init message from the host and updates the client cache.
        Will shield the normal message handler from receiving events until the initialisation succeeded.
        :returns: A List of all other events that were received during initialisation that will now need to be called
        """
        house_memberships = msg['d'].get('house_memberships', 0)

        cached_houses = []  # Only for test purposes for now

        # Additional events that were received during the initialisation and now need to be executed
        additional_events = []
        while len(house_memberships) != len(cached_houses):
            event, data, msg = await self.wait_for_event(handler=self.received_init_event)

            if msg:
                if event == "HOUSE_JOIN":
                    cached_houses.append(data.get('id'))
                    # JSON Caching and other stuff (#53)
                else:
                    additional_events.append(msg)

        for e in additional_events:
            await self.received_message(e)

    async def received_message(self, msg):
        """
        Awaits a new incoming message and handles it.
        Will raise an exception if a close frame was received
        """
        msg = msg.json()
        op, event, d = self._extract_event(msg)

        if op == self.OPCode.CONNECTION_START:
            pass
        elif op == self.OPCode.EVENT:
            logger.debug(f"[WEBSOCKET] Received Websocket Event: {event}")

            if event == 'INIT_STATE':
                # Using a separate function to fetch all initialisation events
                await self.received_init(msg, self.client)
                logger.debug("[WEBSOCKET] Received Init Frame from the Hiven Swarm and initialised the Client Cache")
                self._ready = True
            else:
                pass
                # Message Broker Handling and Rewrite (#54)

            return

        else:
            logger.warning(f"[WEBSOCKET] Received unknown websocket op-code message: {op}: {msg}")

    def _extract_event(self, msg: dict) -> tuple:
        """ Formats the incoming msg and returns it in tuple form """
        return msg.get('op'), msg.get('e'), msg.get('d')
