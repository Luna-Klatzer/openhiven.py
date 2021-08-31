"""
WebSocket file for managing the Hiven Swarm and connection

---

Under MIT License

Copyright © 2020 - 2021 Luna Klatzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Used for type hinting and not having to use annotations for the objects
from __future__ import annotations

import asyncio
import json
import logging
import time
from enum import IntEnum
# Only importing the Objects for the purpose of type hinting and not actual use
from typing import TYPE_CHECKING
from typing import Tuple, Optional, Callable, Any

import aiohttp
from yarl import URL

from .messagebroker import MessageBroker
from ..base_types import HivenObject
from ..exceptions import (RestartSessionError, SessionCreateError,
                          WebSocketClosedError,
                          WebSocketFailedError, KeepAliveError)

if TYPE_CHECKING:
    from ..events import HivenParsers
    from .. import HivenClient

__all__ = ['HivenWebSocket', 'KeepAlive']

logger = logging.getLogger(__name__)


def extract_event(msg: dict) -> Tuple[int, str, dict]:
    """
    Formats the incoming msg and returns it in tuple form

    :param msg: The raw WebSocket Message
    :return: The op-code, event-name and data in tuple form
    """
    return msg.get('op'), msg.get('e'), msg.get('d')


class KeepAlive(HivenObject):
    """ Keep-Alive class managing the heartbeat """
    def __init__(self, ws):
        self.ws: HivenWebSocket = ws
        self._heartbeat: int = ws.heartbeat
        self._task = None
        self._active = False

    @property
    def active(self) -> Optional[bool]:
        """
        Returns whether the KeepAlive class is actively sending heartbeats
        """
        return getattr(self, '_active', False)

    @property
    def task(self) -> Optional[asyncio.Task]:
        """
        The task where the heartbeat is currently located and being sent
        """
        return getattr(self, '_task', None)

    async def _heartbeat_and_sleep(self) -> None:
        """ Sends the heartbeat to Hiven and sleeps """
        await asyncio.wait_for(self.ws.send_heartbeat(), 30)
        await asyncio.sleep(self._heartbeat / 1000)

    async def run(self) -> None:
        """
        Runs the current KeepAlive process in a loop that can be cancelled
        using `KeepAlive.stop()`
        """
        self._active = True
        while self.ws.open:
            try:
                self._task = asyncio.create_task(self._heartbeat_and_sleep())
                await self._task
            except asyncio.CancelledError:
                break
            except Exception as e:
                raise KeepAliveError(
                    "KeepAlive failed to process properly due to an exception"
                    " occurring"
                ) from e
        self._active = False

    async def stop(self) -> None:
        """ Stops the running KeepAlive loop """
        if self._task:
            if not self._task.done():
                self._task.cancel()


class HivenWebSocket(HivenObject):
    """
    WebSocket instance, which establishes, manages and handles the Hiven Swarm
    and its incoming messages and events.
    """
    def __init__(
            self,
            socket: aiohttp.ClientWebSocketResponse,
            *,
            loop: asyncio.AbstractEventLoop,
            log_websocket: bool = False
    ):
        self.endpoint = None
        self.log_websocket = log_websocket

        self._socket = socket
        self._loop = loop
        self._parsers = None
        self._keep_alive = None
        self._message_broker = None
        self._client = None
        self._open = False
        self._ready = False
        self._startup_time = None
        self._connection_start = None
        self._token = None
        self._heartbeat = None
        self._close_timeout = None

        # Close code used to represent the status of the aiohttp websocket
        # after it closed
        self._close_code = None

    @classmethod
    async def create_from_client(
            cls,
            client: HivenClient,
            endpoint: URL,
            close_timeout: int,
            heartbeat: int,
            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
            **kwargs
    ):
        """
        Creates a new WebSocket Instance and starts the Connection to Hiven
        """
        socket: aiohttp.ClientWebSocketResponse
        socket = await client.http.session.ws_connect(
            endpoint.human_repr(), timeout=close_timeout, heartbeat=heartbeat,
            max_msg_size=0
        )
        ws: HivenWebSocket = cls(socket, loop=loop, **kwargs)
        ws._endpoint = endpoint
        ws._parsers = client.parsers
        ws._client = client
        ws._token = client.token
        ws._heartbeat = heartbeat
        ws._close_timeout = close_timeout

        ws._message_broker = MessageBroker(client=client)
        ws._keep_alive = KeepAlive(ws)

        return ws

    class OPCode(IntEnum):
        """ OP-Codes in the Hiven Swarm """
        EVENT = 0
        CONNECTION_START = 1
        AUTH = 2
        HEARTBEAT = 3

    @property
    def token(self) -> str:
        """ The token used to connect to the Hiven-Endpoint """
        return getattr(self, '_token', None)

    @property
    def socket(self) -> aiohttp.ClientWebSocketResponse:
        """ Returns the aiohttp Socket instance """
        return getattr(self, '_socket', None)

    @property
    def client(self) -> HivenClient:
        """ Returns the HivenClient used to initialise this instance """
        return getattr(self, '_client', None)

    @property
    def parsers(self) -> HivenParsers:
        """
        Returns the instance of the Hiven-Parsers which manage and update
        data based on incoming Swarm events
        """
        return getattr(self, '_parsers', None)

    @property
    def message_broker(self) -> MessageBroker:
        """ Returns the Message-Broker managing incoming messages """
        return getattr(self, '_message_broker', None)

    @property
    def keep_alive(self) -> KeepAlive:
        """ Returns the KeepAlive Object instance """
        return getattr(self, '_keep_alive', None)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """ Returns the Asyncio Event-loop """
        return getattr(self, '_loop', None)

    @property
    def startup_time(self) -> Optional[int]:
        """
        Returns the startup time - how long it took from calling to an active
        working connection
        """
        return getattr(self, '_startup_time', None)

    @property
    def connection_start(self) -> Optional[int]:
        """
        Returns the unix-timestamp (seconds) when the connection started
        """
        return getattr(self, '_connection_start', None)

    @property
    def connection_status(self) -> Optional[str]:
        """ Returns the connection status as a string """
        return getattr(self.client.connection, 'connection_status', None)

    @property
    def closing(self) -> bool:
        """
        Returns whether the connection is currently closing.
        Not True if already closed!
        """
        return getattr(self.client.connection, '_closing', None)

    @property
    def open(self) -> bool:
        """ Returns whether the connection is open """
        return getattr(self, '_open', None)

    @property
    def ready(self) -> bool:
        """ Returns whether the Web-Socket has initialised and is ready """
        return getattr(self, '_ready', None)

    @property
    def heartbeat(self) -> Optional[int]:
        """ Heartbeat in ms """
        return getattr(self, '_heartbeat', None)

    @property
    def close_timeout(self) -> Optional[int]:
        """ Set Close-Timeout, which if exceeded will cancel the connection """
        return getattr(self, '_close_timeout', None)

    async def listening_loop(self) -> None:
        """
        Listens infinitely for WebSocket Messages and will trigger events
        accordingly
        """
        while True:
            await self.wait_for_event()

    async def wait_for_event(self, handler: Callable = None) -> Any:
        """
        Waits for an event or websocket message and then triggers appropriately
         the events or raises Exceptions

        Will raise an exception if a close frame was received>

        :param handler: Handler Awaitable that will be executed instead of
        `received_message()` if not None
        """
        msg = await self.socket.receive()

        logger.debug(
            f"[WEBSOCKET] Received WebSocket Message Type '{msg.type.name}'"
        )

        if msg.type == aiohttp.WSMsgType.TEXT:
            return await self._received_message(
                msg) if handler is None else await handler(msg)

        elif msg.type == aiohttp.WSMsgType.BINARY:
            if type(msg) is bytes:
                msg = msg.data.decode("utf-8")
            else:
                raise
            return await self._received_message(
                msg) if handler is None else await handler(msg)

        self._open = False
        self._ready = False
        self.client.connection._connection_status = "CLOSING"
        if msg.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSING,
                aiohttp.WSMsgType.CLOSED
        ):
            # The process is closing so no restart will be scheduled
            if self.closing:
                logger.info(
                    "[WEBSOCKET] Closing the WebSocket Connection and stopping"
                    " the processes"
                )
                raise WebSocketClosedError()
            else:
                logger.error(
                    "[WEBSOCKET] Received close frame from the Server! "
                    "WebSocket will force restart"
                )
                raise RestartSessionError()

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(
                f"[WEBSOCKET] Encountered an Exception in the Websocket! "
                f"{msg.extra}"
            )
            raise WebSocketFailedError(
                "[WEBSOCKET] Encountered an Exception in the Websocket"
            )

    async def _received_message(self, msg: aiohttp.WSMessage) -> None:
        """ Awaits a new incoming message and handles it """
        msg = msg.json()
        opcode, event, data = extract_event(msg)

        if opcode == self.OPCode.CONNECTION_START:
            self._connection_start = time.time()
            self._open = True

        elif opcode == self.OPCode.EVENT:
            logger.debug(f"[WEBSOCKET] Received Websocket Event: {event}")

            if event == 'INIT_STATE':
                await self._received_init(msg)
            else:
                await self.parsers.dispatch(event, data)
            return

        else:
            logger.warning(
                f"[WEBSOCKET] Received unknown websocket op-code message:"
                f" {opcode}: {msg}"
            )

    async def _received_init(self, msg: dict) -> None:
        """
        Receives the init message from the host and updates the client cache.
        Will shield the normal message handler from receiving events until the
        initialisation succeeded.

        :return: A List of all other events that were received during
         initialisation that will now need to be called
        """
        await self.client.call_listeners('init', (), {})

        self.client.connection._connection_status = "OPEN"

        data = msg['d']
        house_memberships = data.get('house_memberships', {})
        self.client.storage.update_primary_data(data)

        additional_events = []
        while len(self.client.storage['houses']) < len(house_memberships):
            ws_event = await self.wait_for_event(
                handler=self._received_init_event
            )

            op, event, d = extract_event(ws_event.json())
            logger.debug(f"[WEBSOCKET] Received Websocket Event: {event}")

            if event == "HOUSE_JOIN":
                self.client.storage.add_or_update_house(d)
            else:
                additional_events.append(ws_event)

        # Executing all additional events that were received during the
        # initialisation and were ignored
        for event in additional_events:
            await self._received_message(event)

        self._startup_time = time.time() - self._connection_start

        logger.debug(
            "[WEBSOCKET] Received Init Frame from the Hiven Swarm and "
            "initialised the Client Cache!"
        )
        logger.info(f"[CLIENT] Ready after {self.startup_time}s")

        # Delaying the receiving process until all ready-state listeners
        # were called
        await self.client.call_listeners('ready', (), {})
        self._ready = True

    async def _received_init_event(
            self, msg: aiohttp.WSMessage
    ) -> aiohttp.WSMessage:
        """
        Only intended for the purpose of initialising the Client!
        Will be called by `received_init` on startup
        """
        msg_dict = msg.json()
        opcode = msg_dict.get('op')

        if opcode == self.OPCode.EVENT:
            return msg
        else:
            logger.warning(
                f"[WEBSOCKET] Received unexpected websocket message: "
                f"{opcode}: {msg}"
            )
            return msg

    async def send_heartbeat(self) -> None:
        """
        Sends a heartbeat with the additional op-code for keeping the
        connection alive
        """
        try:
            await self.socket.send_str(str(json.dumps({
                "op": self.OPCode.HEARTBEAT
            })))
        except Exception as e:
            raise RestartSessionError(
                f"Failed to send heartbeat to WebSocket host!"
            ) from e

    async def send_auth(self) -> None:
        """ Sends the authentication header to the Hiven Endpoint"""
        try:
            await self.socket.send_str(
                json.dumps({
                    "op": self.OPCode.AUTH,
                    "d": {
                        "token": self.token
                    }
                })
            )
        except Exception as e:
            raise SessionCreateError(f"Failed to send auth to the host") from e
