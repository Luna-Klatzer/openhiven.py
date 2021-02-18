"""

Module for the OpenHiven.py Gateway and Connection to Hiven

---

Under MIT License

Copyright © 2020 Frostbyte Development Team

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

from .websocket import *
from .http import *
from .messagebroker import *
from .. import load_env, utils
from ..exception import RestartSessionError, WebSocketClosedError

import aiohttp
import sys
import logging
import os
import typing
import asyncio

logger = logging.getLogger(__name__)

load_env()
DEFAULT_HOST = os.getenv("HIVEN_HOST")
DEFAULT_API_VERSION = os.getenv("HIVEN_API_VERSION")
DEFAULT_HEARTBEAT = int(os.getenv("WS_HEARTBEAT"))
DEFAULT_CLOSE_TIMEOUT = int(os.getenv("WS_CLOSE_TIMEOUT"))


class Connection:
    """ Connection Class used for interaction with the Hiven API and WebSocket Swarm"""

    def __init__(self,
                 client,
                 *,
                 host: typing.Optional[str] = DEFAULT_HOST,
                 api_version: typing.Optional[str] = DEFAULT_API_VERSION,
                 heartbeat: typing.Optional[int] = DEFAULT_HEARTBEAT,
                 close_timeout: typing.Optional[int] = DEFAULT_CLOSE_TIMEOUT,
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None):
        self.client = client
        self.http = None
        self.host = host
        self.api_version = api_version
        self.loop = loop
        self.heartbeat = heartbeat
        self.close_timeout = close_timeout

        self._connection_status = "CLOSED"
        self._ready = False
        self._ws = None
        self._coro = None

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('open', self.open),
            ('host', self.host),
            ('api_version', self.api_version),
            ('open', self.open),
            ('startup_time', self.ws.startup_time),
            ('connection_start', self.ws.connection_start),
            ('heartbeat', self.heartbeat)
        ]
        return '<Connection {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def open(self) -> bool:
        return all((
            getattr(self.http, 'ready', False),
            getattr(self.ws, 'open', False)
        ))

    @property
    def connection_status(self) -> str:
        return getattr(self, '_connection_status', None)

    @property
    def ready(self) -> bool:
        return getattr(self.http, 'ready', False)

    @property
    def ws(self) -> HivenWebSocket:
        return getattr(self, '_ws', None)

    @property
    def coro(self):
        return getattr(self, 'coro', None)

    async def connect(self, restart: bool):
        """ Establishes a connection to Hiven and runs the background processes """
        try:
            self.http = HTTP(self.client.token, host=self.host, api_version=self.api_version, loop=self.loop)
            await self.http.connect()

            self._connection_status = "OPENING"
            while self.connection_status not in ("CLOSING", "CLOSED"):
                try:
                    coro = HivenWebSocket.create_from_client(
                        self.client, close_timeout=self.close_timeout, heartbeat=self.heartbeat, loop=self.loop
                    )
                    ws = await asyncio.wait_for(coro, 30)
                    self._ws = ws
                    await ws.send_auth()
                    await asyncio.gather(ws.listening_loop(), ws.keep_alive.run())

                except RestartSessionError:
                    logger.debug("[CONNECTION] Got a request to restart the WebSocket!")
                    continue

                except WebSocketClosedError:
                    continue

                except Exception as e:
                    logger.error(
                        f"[CONNECTION] Encountered an exception while running the live websocket: "
                        f"\n{sys.exc_info()[0].__name__}: {e}"
                    )
                    if restart is False:
                        raise

                await asyncio.sleep(.05)

            await self.http.close()

        except Exception as e:
            utils.log_traceback(
                level='critical',
                msg="[CONNECTION] Traceback:",
                suffix=f"Failed to keep alive current connection to Hiven: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise

    async def close(self):
        """ Closes the Connection to Hiven and stops the running WebSocket and the Event Processing Loop """
        try:
            self._connection_status = "CLOSING"
            await self.ws.keep_alive.stop()
            await self.ws.socket.close()
            self._connection_status = "CLOSED"

        except Exception as e:
            utils.log_traceback(
                level='critical',
                msg="[CONNECTION] Traceback:",
                suffix=f"Failed to close current connection to Hiven: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise
