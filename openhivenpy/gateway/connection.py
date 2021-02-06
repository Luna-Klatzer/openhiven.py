import asyncio
import logging
import sys
import time
import typing
from functools import wraps
import os

from openhivenpy import utils, load_env

from ..exceptions import exception as errs
from openhivenpy.events import EventHandler
from . import Websocket, HTTP

logger = logging.getLogger(__name__)

__all__ = ('ExecutionLoop', 'Connection')

# Loading the environment variables
load_env()
# Setting the default values to the currently set defaults in the openhivenpy.env file
_default_connection_heartbeat = int(os.getenv("CONNECTION_HEARTBEAT"))
_default_close_timeout = int(os.getenv("CLOSE_TIMEOUT"))


def get_gateway(**kwargs):
    return {
        "host": kwargs.get('host', os.environ.get("HIVEN_HOST")),
        "api_version": kwargs.get('api_version', os.environ.get("HIVEN_API_VERSION")),
    }


class StartupTasks:
    """
    Class intended to inherit all StartupTasks
    """
    pass


class BackgroundTasks:
    """
    Class intended to inherit all BackgroundTasks
    """
    pass


class ExecutionLoop:
    """
    Loop that executes tasks in the background.
    
    Not intended for usage for users yet
    """
    def __init__(self, event_loop: asyncio.AbstractEventLoop = None):
        """
        Object Instance Construction

        :param event_loop: Event loop that will be used to execute all async functions.
        """
        self.event_loop = event_loop
        self._background_tasks = []
        self._background_tasks_handler = BackgroundTasks()
        self._startup_tasks = []
        self._startup_tasks_handler = StartupTasks()
        self._finished_tasks = []

        #
        self._active = False
        self._startup_finished = False

        # Variable that stores the current running_loop => None when not running
        self.running_loop = None

    @property
    def active(self):
        """
        Represents the current status of the loop. If True that means the loop is still running
        """
        return self._active

    @property
    def startup_finished(self):
        """
        Represents the status of the Startup Tasks. If True that means it was successfully executed
        and the execution loop is now running!
        """
        return self._startup_finished

    @property
    def tasks(self):
        """
        List of tasks that are stored in the loop
        """
        return self._background_tasks

    @property
    def startup_tasks(self):
        return self._startup_tasks

    async def start(self) -> None:
        """
        Starts the current execution_loop!

        Warning! Does not return until the loop has finished!
        """

        async def _loop(startup_tasks, tasks):
            """
            Loop coroutine that runs the tasks

            :param startup_tasks: Tasks that will be executed once at the beginning of the bot
            :param tasks: Tasks that will run infinitely in the background
            """
            # Startup Tasks
            self._active = True

            # Startup tasks that only get executed once
            async def startup():
                """
                Tasks that are scheduled to run at the start one time before then running the
                general execution_loop
                """
                try:
                    if not startup_tasks == []:
                        _tasks = []
                        for task_name in startup_tasks:
                            # Fetching the startup_task from the object that stores them
                            async_task = getattr(self._startup_tasks_handler, task_name)
                            # Creating a callable task and appending it to the methods to call
                            _tasks.append(asyncio.create_task(async_task(), name=task_name))

                        # Passing all tasks as args to the event loop
                        await asyncio.gather(*_tasks)

                except asyncio.CancelledError:
                    logger.debug(f"[EXEC-LOOP] Startup tasks were cancelled and stopped unexpectedly!")

                except Exception as e:
                    utils.log_traceback(msg="[EXEC-LOOP] Traceback:",
                                        suffix="Error in startup tasks in the execution loop; \n"
                                               f"{sys.exc_info()[0].__name__}: {e}")

                finally:
                    self._startup_finished = True
                    return

            # Background loop
            async def __background_loop():
                """
                Background Loop for all tasks that will be run in the background infinitely
                """
                if not tasks == []:
                    # Checks whether the loop is supposed to be running
                    while self._active:
                        _tasks = []
                        for task_name in tasks:
                            # Fetching the startup_task from the object that stores them
                            async_task = getattr(self._background_tasks_handler, task_name)
                            # Creating a callable task
                            _tasks.append(asyncio.create_task(async_task(), name=task_name))

                        # Passing all tasks as args to the event loop
                        await asyncio.gather(*_tasks)
                return

            try:
                await asyncio.gather(startup(), __background_loop(), return_exceptions=True)
            except asyncio.CancelledError:
                logger.debug(f"[EXEC-LOOP] Async gather of tasks was cancelled and stopped unexpectedly!")

        self.running_loop = asyncio.create_task(_loop(self._startup_tasks, self._background_tasks))
        try:
            await self.running_loop
        except asyncio.CancelledError:
            logger.debug("[EXEC-LOOP] Async task was cancelled and stopped unexpectedly! "
                         "No more tasks will be executed!")
        except Exception as e:
            utils.log_traceback(msg="[EXEC-LOOP] Traceback:",
                                suffix="Failed to start or keep alive execution_loop; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
        finally:
            self._active = False
            return

    async def stop(self) -> None:
        """
        Forces the current execution_loop to stop!

        Use with caution! Will stop all tasks running in the background and will make ready-state impossible if the
        Client was not ready!
        """
        try:
            if not self.running_loop.cancelled():
                self.running_loop.cancel()

            # Ensuring the tasks stops as soon as possible
            self._active = False
            logger.debug("[EXEC-LOOP] The execution loop was cancelled and stopped")

            # Setting the running_loop to None again!
            self.running_loop = None

        except Exception as e:
            utils.log_traceback(msg="[EXEC-LOOP] Traceback:",
                                suffix="Failed to stop or keep alive execution_loop; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.UnableToClose("Failed to stop or keep alive execution_loop!"
                                     f"> {sys.exc_info()[0].__name__}: {e}")
        finally:
            return

    def add_to_loop(self, func: typing.Awaitable = None):
        """
        Decorator used for registering Tasks for the execution_loop
        
        :param func: Function that should be wrapped and then executed in the Execution Loop
                     Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """

        def decorator(__func):
            @wraps(__func)
            async def wrapper():
                await asyncio.sleep(0.05)  # Sleeping to avoid too many executions at once
                return await __func

            setattr(self._background_tasks_handler, __func.__name__, wrapper)
            self._background_tasks.append(__func.__name__)

            logger.debug(f"[EXEC-LOOP] >> Task {__func.__name__} added to loop")

            return __func  # returning func so it still can be used outside the class

        if func is None:
            return decorator
        else:
            return decorator(func)

    def add_to_startup(self, func: typing.Awaitable = None):
        """
        Decorator used for registering Startup Tasks for the execution_loop
        
        Note! Startup Tasks only get executed one time at start and will not be repeated!
        
        :param func: Function that should be wrapped and then executed at startup in the Execution Loop
                     Only usable if the wrapper is used in the function syntax: 'event(func)'!
        """

        def decorator(__func):
            @wraps(__func)
            async def wrapper():
                await asyncio.sleep(0.05)  # Sleeping to avoid too many executions at once
                return await __func

            setattr(self._startup_tasks_handler, __func.__name__, wrapper)
            self._startup_tasks.append(__func.__name__)

            logger.debug(f"[EXEC-LOOP] >> Startup Task {__func.__name__} added to loop")

            return __func  # returning func so it still can be used outside the class

        if func is None:
            return decorator
        else:
            return decorator(func)


class Connection(Websocket):
    """
    Connection Class that wraps the Websocket and HTTP-Session and their handling
    """

    def __init__(self,
                 token: str,
                 *,
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
        :param event_loop: Event loop that will be used to execute all async functions. Will use 'asyncio.get_event_loop()' to fetch the EventLoop. Will create a new one if no one was created yet
        :param close_timeout: Seconds after the websocket will timeout after the end handshake didn't complete
                              successfully. Defaults to the pre-set environment close_timeout (40)
        :param log_ws_output: Will additionally to normal debug information also log the ws responses
        """
        self._connection_start = None
        self._startup_time = None
        self._initialised = False
        self._ready = False
        self._connection_start = None

        self._connection_status = "CLOSED"

        self._gateway = get_gateway(**kwargs)
        self._host = self._gateway.get('host')
        self._api_version = self._gateway.get('api_version')

        self._event_loop = None
        self._execution_loop = ExecutionLoop(self._event_loop)

        self._token = token
        self._http = None

        super().__init__(event_handler=event_handler,
                         token=token,
                         heartbeat=heartbeat,
                         event_loop=event_loop,
                         close_timeout=close_timeout,
                         log_ws_output=log_ws_output,
                         **self._gateway)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        info = [
            ('open', self.open),
            ('host', self.host),
            ('api_version', self.api_version),
            ('http_ready', self.http.ready),
            ('startup_time', self.startup_time),
            ('connection_start', self.connection_start),
            ('heartbeat', self.heartbeat),
            ('encoding', self.encoding),
            ('ws_url', self.websocket_url),
            ('coro', repr(self.ws_connection))
        ]
        return '<Connection {}>'.format(' '.join('%s=%s' % t for t in info))

    @property
    def user(self):
        # => Also referenced in hiven_client.py
        return getattr(self, '_client_user', None)

    @property
    def host(self) -> str:
        return getattr(self, '_HOST', os.getenv("HIVEN_HOST"))

    @property
    def http(self) -> HTTP:
        return getattr(self, '_http', None)

    @property
    def api_version(self) -> str:
        return getattr(self, '_API_VERSION', os.getenv("HIVEN_API_VERSION"))

    @property
    def connection_status(self) -> str:
        return getattr(self, '_connection_status', "CLOSED")

    @property
    def open(self) -> bool:
        return getattr(self, '_open', False)

    @property
    def initialised(self) -> bool:
        return getattr(self, '_initialised', False)

    @property
    def connection_start(self) -> float:
        return getattr(self, '_connection_start', None)

    @property
    def startup_time(self) -> float:
        return getattr(self, '_startup_time', None)

    @property
    def execution_loop(self) -> ExecutionLoop:
        return getattr(self, '_execution_loop', None)

    @property
    def ready(self) -> bool:
        return getattr(self, '_ready', False)

    @property
    def restart(self) -> bool:
        return getattr(self, '_restart', False)

    async def connect(self, event_loop: asyncio.AbstractEventLoop) -> None:
        """
        Establishes a WebSocket connection to Hiven and starts the HTTP-Session

        :param event_loop: Event loop that will be used to execute all async functions. Defaults to the running loop!
        """
        try:
            # Connection Start variable for later calculation the time how long it took to start
            self._connection_start = time.time()
            self._connection_status = "OPENING"

            self._event_loop = event_loop
            # Creating a new HTTP session
            self._http = HTTP(token=self._token, event_loop=event_loop, **self._gateway)

            # Starting the HTTP Connection to Hiven
            session = await self._http.connect()
            if session:
                # Starting the websocket connection and the execution_loop parallel to avoid
                # that they both interfere each other
                await asyncio.gather(self.ws_connect(session), self._execution_loop.start())

            else:
                raise errs.HivenConnectionError("[CONNECTION] Failed to get connected Client data!")

        except Exception as e:
            utils.log_traceback(msg="[CONNECTION] Traceback:",
                                suffix="Failed to establish the connection to Hiven; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.HivenConnectionError("Failed to establish the connection to Hiven! "
                                            f"> {sys.exc_info()[0].__name__}: {e}")
        except KeyboardInterrupt:
            raise KeyboardInterrupt

        finally:
            self._connection_status = "CLOSED"
            logger.info("[CONNECTION] The Client-Session has been closed! Use connect() or run() to reconnect!")
            return

    # Kills the connection as well as the event loop
    async def destroy(self, reason: str = None, exec_loop=True, block_restart: bool = False) -> None:
        """
        Kills the event loop and the running tasks! 
        
        Deprecated! Will be removed in later versions!

        :param exec_loop: If True closes the execution_loop with the other tasks. Defaults to True
        :param reason: Reason for the call of the closing function
        :param block_restart: If set to True restarting will be blocked entirely and the connection returns
        """
        try:
            logger.info(f"[CONNECTION] Close method called! Reason: {reason} >>"
                        " Destroying current processes and gateway connection!")
            self._connection_status = "CLOSING"

            if not self._lifesignal.cancelled():
                self._lifesignal.cancel()

            if not self._connection_task.cancelled():
                self._connection_task.cancel()

            if exec_loop:
                await self._execution_loop.stop()

            await self._event_loop.shutdown_asyncgens()

            self._connection_status = "CLOSED"
            self._initialised = False

            return

        except Exception as e:
            utils.log_traceback(msg="[CONNECTION] Traceback:",
                                suffix=f"Closing the connection to Hiven failed; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.UnableToClose("Closing the connection to Hiven failed!"
                                     f"> {sys.exc_info()[0].__name__}: {e}")

    async def close(self, reason: str = None, close_exec_loop=True, block_restart: bool = False) -> None:
        """
        Stops the active asyncio task that represents the connection and closes all internal processes!

        :param close_exec_loop: If True closes the execution_loop with the other tasks. Defaults to True
        :param reason: Reason for the call of the closing function
        :param block_restart: If set to True restarting will be blocked entirely and the connection returns
        """
        try:
            logger.info(f"[CONNECTION] Close method called! Reason: {reason} >>"
                        " Closing current processes and gateway connection!")
            self._connection_status = "CLOSING"

            # If the force restart is false it will automatically block attempts to restart!
            if block_restart:
                self._restart = False

            if not self._lifesignal.cancelled():
                self._lifesignal.cancel()

            if not self._connection_task.cancelled():
                self._connection_task.cancel()

            if close_exec_loop:
                await self._execution_loop.stop()

            await self.http.close()

            self._connection_status = "CLOSED"
            self._initialised = False

            return

        except Exception as e:
            utils.log_traceback(msg="[CONNECTION] Traceback:",
                                suffix=f"Closing the connection to Hiven failed; \n"
                                       f"{sys.exc_info()[0].__name__}: {e}")
            raise errs.UnableToClose("Closing the connection to Hiven failed! "
                                     f"> {sys.exc_info()[0].__name__}: {e}")

    # Restarts the connection if it errored or crashed
    async def handler_restart_websocket(self):
        """
        Tries to restart when the websocket encountered an error!
        """
        # Delaying each check
        await asyncio.sleep(0.1)

        # _restart from the inherited websocket
        if self._restart:
            if self.ws_connection.done():
                logger.info(f"[RESTART_HANDLER] Restarting was scheduled at {time.time()}!")
                await self.connect(self._event_loop)
        return
