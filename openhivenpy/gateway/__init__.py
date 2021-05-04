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

import asyncio
import logging
import os
import sys
from typing import Optional

from yarl import URL

from .http import *
from .messagebroker import *
from .websocket import *
from .. import utils, Object
from ..exceptions import RestartSessionError, WebSocketClosedError, WebSocketFailedError, SessionCreateError, \
    KeepAliveError

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = os.getenv("WS_ENDPOINT")
DEFAULT_HOST = os.getenv("HIVEN_HOST")
DEFAULT_API_VERSION = os.getenv("HIVEN_API_VERSION")
DEFAULT_HEARTBEAT = int(os.getenv("WS_HEARTBEAT"))
DEFAULT_CLOSE_TIMEOUT = int(os.getenv("WS_CLOSE_TIMEOUT"))


class Connection(Object):
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
        self._closing = False
        self._closed = False
        self._force_closing = False
        self._ws = None

    def _set_default_properties(self):
        """ Sets the default properties for the Connection class """
        self._connection_status = "CLOSED"
        self._ready = False
        self._closing = False
        self._closed = False
        self._force_closing = False
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

    @property
    def closed(self) -> Optional[bool]:
        return getattr(self, '_closed', None)

    @property
    def socket_closed(self) -> Optional[bool]:
        return getattr(getattr(self.ws, 'socket', None), 'closed', False)

    async def connect(self, restart: bool) -> None:
        """
        Establishes a connection to Hiven and runs the background processes.
        Only closes if forced to using close() or an exception is raised and restart is False
        """
        try:
            self._connection_status = "OPENING"
            self.http = HTTP(self.client, host=self.host, api_version=self.api_version)
            await self.http.connect()

            while not self.socket_closed:
                try:
                    coro = HivenWebSocket.create_from_client(
                        self.client, endpoint=self.endpoint, close_timeout=self.close_timeout, heartbeat=self.heartbeat,
                        loop=self.loop
                    )
                    self._ws = await asyncio.wait_for(coro, 30)
                    await self.ws.send_auth()

                    self._closed = False
                    await asyncio.gather(
                        self.ws.listening_loop(), self.ws.keep_alive.run(), self.ws.message_broker.run()
                    )

                except asyncio.TimeoutError:
                    # If the timeout is hit the connection might not be possible or unstable, so a warning needs to be
                    # thrown
                    utils.log_traceback(
                        brief="[CONNECTION] Ignoring Timeout Traceback:",
                        exc_info=sys.exc_info()
                    )
                    logger.warning(
                        "[CONNECTION] The websocket exceeded the timeout limit! Connection will be restarted!"
                    )

                except RestartSessionError:
                    # Encountered an exception inside the receive process of the WebSocket and
                    # the system should restart to make sure the user can continue to use the Client
                    logger.debug("[CONNECTION] Received a request to restart the WebSocket!")
                    continue

                except (WebSocketClosedError, KeepAliveError):
                    continue

                except (Exception, WebSocketFailedError) as e:
                    if self.connection_status == "OPENING":
                        utils.log_traceback(
                            brief="[CONNECTION] Encountered an exception while initialising the websocket",
                            exc_info=sys.exc_info()
                        )
                    else:
                        utils.log_traceback(
                            brief="[CONNECTION] Encountered an exception while running the core modules ",
                            exc_info=sys.exc_info()
                        )

                    if restart is False:
                        raise RuntimeError("Websocket encountered an exception while running") from e

        except KeyboardInterrupt:
            await self.http.close()
            await self.close(force=True)
            return

        except Exception as e:
            utils.log_traceback(
                level='critical',
                brief=f"Failed to keep alive current connection to Hiven:",
                exc_info=sys.exc_info()
            )
            raise SessionCreateError(f"Failed to establish HivenClient session") from e
        else:
            await self.ws.keep_alive.stop()
            await self.http.close()

            while self.ws.keep_alive.active:
                await asyncio.sleep(.05)

            self.client.connection._connection_status = "CLOSED"
            self._closed = True

            del self._ws
            self._set_default_properties()

    async def close(self, force: bool = False) -> None:
        """
        Closes the Connection to Hiven and stops the running WebSocket and the Event Processing Loop

        :param force: If set to True the running event-listener workers will be forced closed, which may lead to running
                      code of event-listeners being stopped while performing actions. If False the stopping will wait
                      for all running event_listeners to finish
        """
        try:
            self._connection_status = "CLOSING"
            self._closing = True
            self._force_closing = force

            logger.info(f"[CONNECTION] Received force {'close ' if force else ''}call to stop the running Client")

            await self.ws.socket.close()

            while not self.socket_closed:
                await asyncio.sleep(.05)

            if force:
                # Forcing the loop to stop making all tasks be cancelled
                await self.ws.message_broker.close_loop()
            else:
                # Waiting until the message_broker is closed
                while self.ws.message_broker.running:
                    await asyncio.sleep(.05)

            self._closing = False

        except Exception as e:
            utils.log_traceback(
                level='critical',
                brief=f"Failed to close current connection to Hiven",
                exc_info=sys.exc_info()
            )
            raise RuntimeError("Failed to stop client due to an exception occurring") from e
