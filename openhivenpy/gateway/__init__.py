"""

Module for the OpenHiven.py Gateway and Connection to Hiven

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

from .websocket import *
from .http import *
from .messagebroker import *
from .. import load_env_vars, utils
from ..exceptions import RestartSessionError, WebSocketClosedError, WebSocketFailedError, SessionCreateError

import sys
import logging
import os
import asyncio
from typing import Optional, NoReturn
from yarl import URL

logger = logging.getLogger(__name__)

load_env_vars()
DEFAULT_ENDPOINT = os.getenv("WS_ENDPOINT")
DEFAULT_HOST = os.getenv("HIVEN_HOST")
DEFAULT_API_VERSION = os.getenv("HIVEN_API_VERSION")
DEFAULT_HEARTBEAT = int(os.getenv("WS_HEARTBEAT"))
DEFAULT_CLOSE_TIMEOUT = int(os.getenv("WS_CLOSE_TIMEOUT"))


class Connection:
    """ Connection Class used for interaction with the Hiven API and WebSocket Swarm"""

    def __init__(
        self,
        client,
        *,
        host: Optional[str] = DEFAULT_HOST,
        api_version: Optional[str] = DEFAULT_API_VERSION,
        heartbeat: Optional[int] = DEFAULT_HEARTBEAT,
        close_timeout: Optional[int] = DEFAULT_CLOSE_TIMEOUT
    ):
        self.client = client
        self.http = None
        self._host = host if heartbeat is not None else DEFAULT_HOST
        self._api_version = api_version if heartbeat is not None else DEFAULT_API_VERSION
        self._heartbeat = heartbeat if heartbeat is not None else DEFAULT_HEARTBEAT
        self._close_timeout = close_timeout if heartbeat is not None else DEFAULT_CLOSE_TIMEOUT
        self._endpoint = URL(DEFAULT_ENDPOINT)

        self._connection_status = "CLOSED"
        self._ready = False
        self._ws = None

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:
        info = [
            ('ready', self.ready),
            ('host', self.host),
            ('endpoint', self.endpoint.human_repr()),
            ('startup_time', self.ws.startup_time),
            ('connection_start', self.ws.connection_start),
            ('heartbeat', self.heartbeat)
        ]
        return '<Connection {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def ready(self) -> bool:
        return all((
            getattr(self.http, 'ready', False),
            getattr(self.ws, 'ready', False)
        ))

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        return getattr(self.client, 'loop', None)

    @property
    def host(self) -> Optional[str]:
        return getattr(self, '_host', None)

    @property
    def api_version(self) -> Optional[str]:
        return getattr(self, '_api_version', None)

    @property
    def connection_status(self) -> Optional[str]:
        return getattr(self, '_connection_status', None)

    @property
    def endpoint(self) -> Optional[URL]:
        return getattr(self, '_endpoint', None)

    @property
    def startup_time(self) -> Optional[int]:
        return getattr(self.ws, '_startup_time', None)

    @property
    def ws(self) -> Optional[HivenWebSocket]:
        return getattr(self, '_ws', None)

    @property
    def heartbeat(self) -> Optional[int]:
        return getattr(self, '_heartbeat', None)

    @property
    def close_timeout(self) -> Optional[int]:
        return getattr(self, '_close_timeout', None)

    async def connect(self, restart: bool) -> NoReturn:
        """ Establishes a connection to Hiven and runs the background processes """
        try:
            self.http = HTTP(self.client, host=self.host, api_version=self.api_version)
            await self.http.connect()

            self._connection_status = "OPENING"
            while self.connection_status not in ("CLOSING", "CLOSED"):
                try:
                    coro = HivenWebSocket.create_from_client(
                        self.client, endpoint=self.endpoint, close_timeout=self.close_timeout, heartbeat=self.heartbeat,
                        loop=self.loop
                    )
                    self._ws = await asyncio.wait_for(coro, 30)
                    await self.ws.send_auth()
                    await asyncio.gather(
                        self.ws.listening_loop(), self.ws.keep_alive.run(), self.ws.message_broker.run()
                    )

                except RestartSessionError:
                    # Encountered an exception inside the receive process of the WebSocket and
                    # the system should restart to make sure the user can continue to use the Client
                    logger.debug("[CONNECTION] Got a request to restart the WebSocket!")
                    continue

                except WebSocketClosedError:
                    # Received close frame which can means the connection suddenly stopped/failed or the user
                    # used close to close the connection. If that's the case using continue will make the loop
                    # stop since the connection_status is CLOSING
                    continue

                except (Exception, WebSocketFailedError) as e:
                    logger.error(
                        f"[CONNECTION] Encountered an exception while running the live websocket: "
                        f"\n{sys.exc_info()[0].__name__}: {e}"
                    )
                    if restart is False:
                        raise

                await asyncio.sleep(.05)

        except KeyboardInterrupt:
            await self.http.close()
            await self.close(force=True)
            return

        except Exception as e:
            utils.log_traceback(
                level='critical',
                msg="[CONNECTION] Traceback:",
                suffix=f"Failed to keep alive current connection to Hiven: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise SessionCreateError(f"Failed to establish HivenClient session! > {sys.exc_info()[0].__name__}: {e}")
        else:
            await self.http.close()

    async def close(self, force: bool = False) -> NoReturn:
        """
        Closes the Connection to Hiven and stops the running WebSocket and the Event Processing Loop

        :param force: If set to True the running event-listener workers will be forced closed, which may lead to running
                      code of event-listeners being stopped while performing actions. If False the stopping will wait
                      for all running event_listeners to finish
        """
        try:
            self._connection_status = "CLOSING"
            await self.ws.keep_alive.stop()
            await self.ws.socket.close()
            if force:
                if self.ws.message_broker.running_loop:
                    if self.ws.message_broker.running_loop.cancelled():
                        self.ws.message_broker.running_loop.cancel()

            # Waiting until the message_broker is closed
            while self.ws.message_broker.running:
                await asyncio.sleep(.05)

            self._connection_status = "CLOSED"

        except Exception as e:
            utils.log_traceback(
                level='critical',
                msg="[CONNECTION] Traceback:",
                suffix=f"Failed to close current connection to Hiven: \n{sys.exc_info()[0].__name__}: {e}!"
            )
            raise
