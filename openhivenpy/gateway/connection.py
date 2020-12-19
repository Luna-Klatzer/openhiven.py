import asyncio
import logging
import sys
import time
from functools import wraps
import os
import openhivenpy.exceptions as errs
from openhivenpy.types import Client
from openhivenpy.events import EventHandler
from . import Websocket, HTTP

logger = logging.getLogger(__name__)

__all__ = ('ExecutionLoop', 'Connection')


def _get_args(**kwargs):
    return {
        "host": kwargs.get('host', os.environ.get("HIVEN_HOST")),
        "api_version": kwargs.get('api_version', os.environ.get("HIVEN_API_VERSION")),
        "heartbeat": kwargs.get('heartbeat', int(os.environ.get("CONNECTION_HEARTBEAT"))),
        "close_timeout": kwargs.get('close_timeout', int(os.environ.get("CLOSE_TIMEOUT"))),
        "event_loop": kwargs.get('event_loop'),
        "restart": kwargs.get('restart', False),
        "log_ws_output": kwargs.get('log_ws_output', False)
    }


class ExecutionLoop:
    """`openhivenpy.gateway.ExecutionLoop` 
    
    ExecutionLoop
    ~~~~~~~~~~~~~
    
    Loop that executes tasks in the background.
    
    Not yet ready for users
    
    Parameter:
    ----------
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    
    def __init__(self, event_loop: asyncio.AbstractEventLoop, **kwargs):
        self.event_loop = event_loop
        self._tasks = []
        self._startup_tasks = []
        self._finished_tasks = []
        self._startup_methods = self.StartupTasks()
        self._active = False
        self._startup_finished = False
        self.exec_loop = kwargs.get('exec_loop')
        
    class StartupTasks:
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
        return self.startup_finished
    
    @property
    def tasks(self):
        """
        List of tasks that are stored in the loop
        """
        return self._tasks
    
    @property
    def startup_tasks(self):
        return self._startup_tasks
        
    async def start(self) -> None:
        """`openhivenpy.gateway.ExecutionLoop.start()` 
        
        Starts the current execution_loop
        
        """        
        async def execute_loop(startup_tasks, tasks) -> None:
            # Startup Tasks
            self._active = True
            
            # Startup tasks that only get executed once
            async def startup():
                try:
                    if not startup_tasks == []:
                        methods_to_call = []
                        for task in startup_tasks:
                            task = getattr(self._startup_methods, task)
                            methods_to_call.append(self.event_loop.create_task(task()))
                            
                        await asyncio.gather(*methods_to_call, loop=self.event_loop)
                        
                except asyncio.CancelledError:
                    logger.debug(f"[EXEC-LOOP] Startup tasks were cancelled and stopped unexpectedly!")

                except Exception as e:
                    logger.error(f"[EXEC-LOOP] Error in startup tasks in the execution loop!" 
                                 f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

                finally:
                    self._startup_finished = True
                    
            # Background loop
            async def loop():
                if not tasks == []:
                    # Checks whether the loop is supposed to be running
                    while self._active:
                        methods_to_call = []
                        for task in tasks:
                            methods_to_call.append(self.event_loop.create_task(getattr(self, task)()))
                        
                        await asyncio.gather(*methods_to_call, loop=self.event_loop)
            try:
                result = await asyncio.gather(startup(), loop(), return_exceptions=True)
            except asyncio.CancelledError as e:
                logger.debug(f"[EXEC-LOOP] Async gather of tasks was cancelled and stopped unexpectedly!")

        self.exec_loop = self.event_loop.create_task(execute_loop(self._startup_tasks, self._tasks))
        try:
            await self.exec_loop
        except asyncio.CancelledError as e:
            logger.debug("[EXEC-LOOP] Async task was cancelled and stopped unexpectedly! "
                         "No more tasks will be executed!")
        except Exception as e:
            logger.error("[EXEC-LOOP] Failed to start or keep alive execution_loop!" 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            self._active = False
            return

    async def stop(self) -> None:
        """`openhivenpy.gateway.ExecutionLoop.stop()`
        
        Stops the current execution_loop
        
        """
        try:
            if not self.exec_loop.cancelled():
                self.exec_loop.cancel()
            
            # Ensuring the tasks stops as soon as possible
            self._active = False
            logger.debug("[EXEC-LOOP] The execution loop was cancelled and stopped")
            
        except Exception as e:
            logger.critical(f"Failed to stop or keep alive execution_loop!" 
                            f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to stop or keep alive execution_loop!" 
                                     f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return 
        
    def add_to_loop(self, func=None):
        """`openhivenpy.gateway.ExecutionLoop.create_task`
        
        Decorator used for registering Tasks for the execution_loop
        
        Parameter:
        ----------
        
        func: `function` - Function that should be wrapped and then executed in the Execution Loop
                            Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs):
                await asyncio.sleep(0.05)
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper)
            self._tasks.append(func.__name__)
            
            logger.debug(f"[EXEC-LOOP] >> Task {func.__name__} added to loop")

            return func  # returning func means func can still be used normally

        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def add_to_startup(self, func=None):
        """`openhivenpy.gateway.ExecutionLoop.create_task`
        
        Decorator used for registering Startup Tasks for the execution_loop
        
        Note! Startup Tasks only get executed one time at start and will not be repeated!
        
        Parameter:
        ----------
        
        func: `function` - Function that should be wrapped and then executed at startup in the Execution Loop
                        Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs):
                await asyncio.sleep(0.05)
                return await func(*args, **kwargs)
            
            setattr(self._startup_methods, func.__name__, wrapper)
            self._startup_tasks.append(func.__name__)
            
            logger.debug(f"[EXEC-LOOP] >> Startup Task {func.__name__} added to loop")

            return func # returning func means func can still be used normally

        if func is None:
            return decorator
        else:
            return decorator(func)


class Connection(Websocket, Client):
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
                            didn't complete successfully. Defaults to `20`
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    def __init__(self, token: str, event_handler: EventHandler, **kwargs):

        self._connection_start = None
        self._startup_time = None
        self._initialized = False
        self._ready = False
        self._connection_start = None
        
        self._connection_status = "CLOSED"
        
        self._init_args = _get_args(**kwargs)
        self._HOST = self._init_args.get('host')
        self._API_VERSION = self._init_args.get('api_version')

        self._event_loop = self._init_args.get('event_loop')
        self._execution_loop = ExecutionLoop(self._event_loop)
        
        self._token = token
        self.http = HTTP(loop=self._event_loop, token=token, **self._init_args)
        self.http._ready = False
        
        super().__init__(event_handler=event_handler, token=token, **self._init_args)

    @property
    def host(self) -> str:
        return self._HOST

    @property
    def api_version(self) -> str:
        return self._API_VERSION
        
    @property
    def connection_status(self) -> str:
        return self._connection_status

    @property
    def open(self) -> bool:
        return self._open

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def connection_start(self) -> float:
        return self._connection_start

    @property
    def startup_time(self) -> float:
        return self._startup_time
    
    @property
    def execution_loop(self) -> ExecutionLoop:
        return self._execution_loop

    @property
    def ready(self) -> bool:
        return self._ready
    
    async def connect(self) -> None:
        """`openhivenpy.gateway.Connection.connect()`

        Establishes a connection to Hiven
        
        """
        try:
            # Connection Start variable for later calculation the time how long it took to start
            self._connection_start = time.time()
            self._connection_status = "OPENING"
            
            # Starting the HTTP Connection to Hiven
            session = await self.http.connect()
            if session:
                # Creating the restart task if true
                if self._restart:
                    self._execution_loop.add_to_startup(self._restart_websocket)

                await asyncio.gather(self.ws_connect(session), self._execution_loop.start())
            else:
                msg = "[CONNECTION] Failed to get connected Client data!"
                logger.critical(msg)
                raise errs.HivenConnectionError(msg)

        except Exception as e:
            logger.critical(f"Error while trying to establish the connection to Hiven! " 
                            f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.HivenConnectionError(f"Error while trying to establish the connection to Hiven! " 
                                            f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            
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
            logger.critical(f"Closing the connection to Hiven failed!" 
                            f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
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
            
            if not kwargs.get('restart', False):
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
            logger.critical(f"Closing the connection to Hiven failed! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(e)
        
    # Restarts the connection if it errored or crashed
    async def _restart_websocket(self):
        """`openhivenpy.gateway.Connection._restart_websocket()`
  
        Tries to restart when the websocket occurred an error!
        
        If the restart failed again the program stops!
        
        """
        # Delaying the checks so to avoid the case that the user closes the connection 
        # and it restarts because the restart wasn't deactivated
        await asyncio.sleep(0.25)
        # _restart from the inherited websocket
        if self._restart:
            if self.ws_connection.done():
                self._connection_status = "OPENING"
                
                await self.close(exec_loop=False)

                self.http = HTTP(loop=self._event_loop, token=self._token, **self._init_args)
                self.http._ready = False

                logger.info(f"Restarting was scheduled at {time.time()}!")
                await self.connect()
        return
