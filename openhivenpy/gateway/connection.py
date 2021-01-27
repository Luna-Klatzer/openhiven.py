import asyncio
import logging
import sys
import time
from functools import wraps
import os

import openhivenpy.exceptions as errs
from openhivenpy.events import EventHandler
from . import Websocket, HTTP

logger = logging.getLogger(__name__)

__all__ = ('ExecutionLoop', 'Connection')


def _get_connection_args(**kwargs):
    return {
        "host": kwargs.get('host', os.environ.get("HIVEN_HOST")),
        "api_version": kwargs.get('api_version', os.environ.get("HIVEN_API_VERSION")),
        "heartbeat": kwargs.get('heartbeat', int(os.environ.get("CONNECTION_HEARTBEAT"))),
        "close_timeout": kwargs.get('close_timeout', int(os.environ.get("CLOSE_TIMEOUT"))),
        "event_loop": kwargs.get('event_loop'),
        "log_ws_output": kwargs.get('log_ws_output', False)
    }


class ExecutionLoop:
    r"""`openhivenpy.gateway.ExecutionLoop`
    
    Loop that executes tasks in the background.
    
    Not yet ready for users

    """
    def __init__(self, event_loop: asyncio.AbstractEventLoop = None, **kwargs):
        """`openhivenpy.gateway.ExecutionLoop.__init__()`

        Object Instance Construction

        :param event_loop: Event loop that will be used to execute all async functions.
        :param exec_loop:
        """
        self.event_loop = event_loop
        self._background_tasks = []
        self._background_tasks_handler = self.BackgroundTasks()
        self._startup_tasks = []
        self._startup_tasks_handler = self.StartupTasks()
        self._finished_tasks = []

        #
        self._active = False
        self._startup_finished = False

        # Variable that stores the current running_loop => None when not running
        self.running_loop = None

    class StartupTasks:
        pass

    class BackgroundTasks:
        pass

    @property
    def active(self):
        """
        Represents the current status of the loop. If `True` that means the loop is still running
        """
        return self._active

    @property
    def startup_finished(self):
        """
        Represents the status of the Startup Tasks. If `True` that means it was successfully executed
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
        """`openhivenpy.gateway.ExecutionLoop.start()` 
        
        Starts the current execution_loop!

        Warning! Does not return until the loop has finished!
        
        """

        async def _loop(startup_tasks, tasks) -> None:
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
                    logger.error(f"[EXEC-LOOP] Error in startup tasks in the execution loop!"
                                 f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

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
            logger.error("[EXEC-LOOP] Failed to start or keep alive execution_loop!"
                         f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            self._active = False
            return

    async def stop(self) -> None:
        r"""`openhivenpy.gateway.ExecutionLoop.stop()`
        
        Forces the current execution_loop to stop!

        Only use if you know what you are doing since it can break tasks that are needed for running!
        
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
            logger.critical(f"[EXCE-LOOP] Failed to stop or keep alive execution_loop!"
                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to stop or keep alive execution_loop!"
                                     f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return

    def add_to_loop(self, func=None):
        r"""`openhivenpy.gateway.ExecutionLoop.add_to_loop()`
        
        Decorator used for registering Tasks for the execution_loop
        
        :param func: Function that should be wrapped and then executed in the Execution Loop
                     Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """

        def decorator(__func):
            @wraps(__func)
            async def wrapper(*args, **kwargs):
                await asyncio.sleep(0.05)
                return await __func(*args, **kwargs)

            setattr(self._background_tasks_handler, __func.__name__, wrapper)
            self._background_tasks.append(__func.__name__)

            logger.debug(f"[EXEC-LOOP] >> Task {__func.__name__} added to loop")

            return __func  # returning func so it still can be used outside the class

        if func is None:
            return decorator
        else:
            return decorator(func)

    def add_to_startup(self, func=None):
        r"""`openhivenpy.gateway.ExecutionLoop.add_to_startup()`
        
        Decorator used for registering Startup Tasks for the execution_loop
        
        Note! Startup Tasks only get executed one time at start and will not be repeated!

        
        :param func: Function that should be wrapped and then executed at startup in the Execution Loop
                     Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """

        def decorator(__func):
            @wraps(__func)
            async def wrapper(*args, **kwargs):
                await asyncio.sleep(0.05)
                return await __func(*args, **kwargs)

            setattr(self._startup_tasks_handler, __func.__name__, wrapper)
            self._startup_tasks.append(__func.__name__)

            logger.debug(f"[EXEC-LOOP] >> Startup Task {__func.__name__} added to loop")

            return __func  # returning func so it still can be used outside the class

        if func is None:
            return decorator
        else:
            return decorator(func)


class Connection(Websocket):
    """`openhivenpy.gateway.Connection` 
    
    Connection
    ~~~~~~~~~~
    
    Class that wraps the Websocket, HTTP and the Data in the current connection to one class.
    
    Inherits from Websocket and the type Client
    
    Parameter:
    ----------
    
    restart: `bool` - If set to True the process will restart if Error Code 1011 or 1006 is thrown
    
    host: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'api.hiven.io' 
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven.
                    Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    log_ws_output: `bool` - Will additionally to normal debug information also log the ws responses
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake
                            didn't complete successfully. Defaults to `40`
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """

    def __init__(self, token: str, event_handler: EventHandler, **kwargs):
        self._connection_start = None
        self._startup_time = None
        self._initialized = False
        self._ready = False
        self._connection_start = None

        self._connection_status = "CLOSED"

        self._init_args = _get_connection_args(**kwargs)
        self._HOST = self._init_args.get('host')
        self._API_VERSION = self._init_args.get('api_version')

        self._event_loop = None
        self._execution_loop = ExecutionLoop(self._event_loop)

        self._token = token
        self._http = None  # Will be created later!

        super().__init__(event_handler=event_handler, token=token, **self._init_args)

    def __str__(self) -> str:
        return str(repr(self))

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
        return getattr(self, '_USER', None)

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
    def initialized(self) -> bool:
        return getattr(self, '_initialized', False)

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
        """`openhivenpy.gateway.Connection.connect()`

        Establishes a connection to Hiven

        Parameter:
        ----------

        event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions.
                                                            Defaults to running loop!


        """
        try:
            # Connection Start variable for later calculation the time how long it took to start
            self._connection_start = time.time()
            self._connection_status = "OPENING"

            self._event_loop = event_loop
            # Creating a new HTTP session!
            self._http = HTTP(loop=event_loop, token=self._token, **self._init_args)

            # Starting the HTTP Connection to Hiven
            session = await self._http.connect()
            if session:
                # Running ws_connect and the execution_loop in the background
                await asyncio.gather(self.ws_connect(session), self._execution_loop.start())
            else:
                msg = "[CONNECTION] Failed to get connected Client data!"
                logger.critical(msg)
                raise errs.HivenConnectionError(msg)

        except Exception as e:
            logger.critical(f"[CONNECTION] Failed to establish the connection to Hiven! "
                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HivenConnectionError(f"Failed to establish the connection to Hiven! "
                                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")

        finally:
            self._connection_status = "CLOSED"
            return

    # Kills the connection as well as the event loop
    async def destroy(self, exec_loop=True, **kwargs) -> None:
        """`openhivenpy.gateway.Connection.destroy()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw `RuntimeError` if the Client was started in a coroutine or if future
        coroutines are going to get executed!

        Parameter
        ~~~~~~~~

        exec_loop: `bool` - If True closes the execution_loop with the other tasks. Defaults to True

        reason: `str` - Reason that will be logged

        """
        try:
            logger.info(f"[CONNECTION] Close method called! Reason: {kwargs.get('reason', 'None')} >>"
                        " Destroying current processes and gateway connection!")
            self._connection_status = "CLOSING"

            if not self._lifesignal.cancelled():
                self._lifesignal.cancel()

            if not self._connection.cancelled():
                self._connection.cancel()

            if exec_loop:
                await self._execution_loop.stop()

            await self._event_loop.shutdown_asyncgens()

            self._connection_status = "CLOSED"
            self._initialized = False

            return

        except Exception as e:
            logger.critical(f"[CONNECTION] Closing the connection to Hiven failed!"
                            f"> {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(e)

    async def close(self, exec_loop=True, **kwargs) -> None:
        """`openhivenpy.gateway.Connection.close()`
        
        Stops the active asyncio task that represents the connection.
        
        Parameter
        ~~~~~~~~
        
        exec_loop: `bool` - If True closes the execution_loop with the other tasks. Defaults to True

        reason: `str` - Reason that will be logged

        """
        try:
            logger.info(f"[CONNECTION] Close method called! Reason: {kwargs.get('reason', 'None')} >>"
                        " Closing current processes and gateway connection!")
            self._connection_status = "CLOSING"

            # If the force restart is false it will automatically block attempts to restart!
            if kwargs.get('restart', False) is False:
                self._restart = False

            if not self._lifesignal.cancelled():
                self._lifesignal.cancel()

            if not self._connection.cancelled():
                self._connection.cancel()

            if exec_loop:
                await self._execution_loop.stop()

            await self.http.close()

            self._connection_status = "CLOSED"
            self._initialized = False

            return

        except Exception as e:
            logger.critical(
                f"[CONNECTION] Closing the connection to Hiven failed! > {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(e)

    # Restarts the connection if it errored or crashed
    async def handler_restart_websocket(self):
        """`openhivenpy.gateway.Connection.handler_restart_websocket()`
  
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
