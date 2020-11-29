import asyncio
import logging
import sys
import time
from functools import wraps

import openhivenpy.exceptions as errs
from openhivenpy.types import Client
from openhivenpy.events import EventHandler
from . import Websocket, HTTPClient

logger = logging.getLogger(__name__)

__all__ = ('ExecutionLoop', 'Connection')

def _get_args(**kwargs):
    return {
        "api_url": kwargs.get('api_url', "https://api.hiven.io"),
        "api_version": kwargs.get('api_version', "v1"),
        "heartbeat": kwargs.get('heartbeat', 30000),
        "ping_timeout": kwargs.get('ping_timeout', 100),
        "close_timeout": kwargs.get('close_timeout', 20),
        "ping_interval": kwargs.get('ping_interval', None),
        "event_loop": kwargs.get('event_loop'),
        "restart": kwargs.get('restart', False)
    }

class ExecutionLoop():
    """`openhivenpy.gateway.ExecutionLoop` 
    
    ExecutionLoop
    ~~~~~~~~~~~~~
    
    Loop that executs tasks in the background.
    
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
        self.exec_loop = None
        
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
        Reprents the status of the Startup Tasks. If `True` that means it was successfully executed and the normal loop is now running!
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
                        
                except asyncio.CancelledError as e:
                    logger.debug(f"The startup tasks loop unexpectedly stopped while running! Probably caused by an error or automatic/forced closing!")
                except Exception as e:
                    logger.error(f"Error in startup tasks in the execution loop! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
    
                finally:
                    self._startup_finished = True
                    
            # Background loop
            async def loop():
                if not tasks == []:
                    # Checks whetever the loop is supposed to be running
                    while self._active:
                        methods_to_call = []
                        for task in tasks:
                            methods_to_call.append(self.event_loop.create_task(getattr(self, task)()))
                        
                        await asyncio.gather(*methods_to_call, loop=self.event_loop)
                        
            await asyncio.gather(startup(), loop())
            
        self.exec_loop = self.event_loop.create_task(execute_loop(self._startup_tasks, self._tasks))
        try:
            await self.exec_loop
        except asyncio.CancelledError:
            logger.debug("Execution loop was cancelled! No more tasks will be executed!")
        except Exception as e:
            logger.error(f"Failed to start or keep alive execution_loop! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            self._active = False
            return

    async def stop(self) -> None:
        """`openhivenpy.gateway.ConnectionLoop.stop()` 
        
        Stops the current execution_loop
        
        """
        try:
            if not self.exec_loop.cancelled():
                self.exec_loop.cancel()
            
            # Ensuring the tasks stops as soon as possible
            self._active = False
            logger.debug("The execution loop was stopped and will now return!")
            
        except Exception as e:
            logger.critical(f"Failed to stop or keep alive execution_loop! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to stop or keep alive execution_loop! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return 
        
    def create_task(self, func=None):
        """`openhivenpy.gateway.ConnectionLoop.create_task` 
        
        Decorator used for registering Tasks for the execution_loop
        
        Parameter:
        ----------
        
        func: `function` - Function that should be wrapped. Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self, func.__name__, wrapper)
            self._tasks.append(func.__name__)
            
            logger.debug(f"Taks {func.__name__} added to loop")

            return func # returning func means func can still be used normally

        if func == None:    
            return decorator
        else:
            return decorator(func)
    
    def create_one_time_task(self, func=None):
        """`openhivenpy.gateway.ConnectionLoop.create_task` 
        
        Decorator used for registering Startup Tasks for the execution_loop
        
        Note! Startup Tasks only get executed one time at start and will not be repeated!
        
        Parameter:
        ----------
        
        func: `function` - Function that should be wrapped. Only usable if the wrapper is used in the function syntax: 'event(func)'!
        
        """
        def decorator(func):
            @wraps(func) 
            async def wrapper(*args, **kwargs): 
                return await func(*args, **kwargs)
            
            setattr(self._startup_methods, func.__name__, wrapper)
            self._startup_tasks.append(func.__name__)
            
            logger.debug(f"Startup Taks {func.__name__} added to loop")

            return func # returning func means func can still be used normally

        if func == None:    
            return decorator
        else:
            return decorator(func)


class Connection(Websocket, Client):
    """`openhivenpy.gateway.Connection` 
    
    Connection
    ~~~~~~~~~~
    
    Class that wraps the Websocket, HTTPClient and the Data in the current connection to one class.
    
    Inherits from Websocket and the type Client
    
    Parameter:
    ----------
    
    restart: `bool` - If set to True the process will restart if Error Code 1011 or 1006 is thrown
    
    api_url: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'https://api.hiven.io' 
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    ping_timeout: `int` - Seconds after the websocket will timeout after no succesful pong response. More information on the websockets documentation. Defaults to `100`
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake didn't complete successfully. Defaults to `20`
    
    ping_interval: `int` - Interval for sending pings to the server. Defaults to `None` because else the websocket would timeout because the Hiven Websocket does not give a response
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    def __init__(self, token: str, event_handler: EventHandler, **kwargs):
        
        self._open = False
        self._closed = True

        self._connection_start = None
        self._startup_time = None
        self._initialized = False
        self._ready = False
        self._connection_start = None
        
        self._connection_status = "CLOSED"
        
        self._init_args = _get_args(**kwargs)
        self._API_URL = self._init_args.get('api_url')
        self._API_VERSION = self._init_args.get('api_version')

        self._event_loop = self._init_args.get('event_loop')
        self._execution_loop = ExecutionLoop(self._event_loop)
        
        self._token = token
        self.http_client = HTTPClient(loop=self._event_loop, token=token, **self._init_args)
        self.http_client.http_ready = False
        
        super().__init__(event_handler=event_handler, token=token, **self._init_args)

    @property
    def api_url(self) -> str:
        return self._API_URL

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
    def initalized(self) -> bool:
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
            
            # Starting the HTTPClient Connection to Hiven
            client_data = await self.http_client.connect()
            
            # Updating the client data based on the response
            await super().update_client_user_data(client_data['data'])
            
            self._execution_loop.create_task(self._restart_websocket)
            
            # Starting the event loop with the websocket
            await asyncio.gather(self.ws_connect(), self._execution_loop.start())
            
        except Exception as e:
            logger.critical(f"Error while trying to establish the connection to Hiven! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.ConnectionError(f"Error while trying to establish the connection to Hiven! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            
        finally:
            self._connection_status = "CLOSED"    
            return
        
        
    # Kills the connection as well as the event loop
    async def destroy(self) -> None:
        """`openhivenpy.gateway.Connection.destroy()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw `RuntimeError` if the Client was started in a courountine or if future courountines are going to get executed!
        
        """
        
        try:
            logger.info("Closing connection!")
            self._connection_status = "CLOSING"
            
            if not self._lifesignal.cancelled():
                self._lifesignal.cancel()
            
            if not self._connection.cancelled():
                self._connection.cancel()
            
            await self._event_loop.shutdown_asyncgens()
            self._event_loop.stop()
            self._event_loop.close()
            
            self._connection_status = "CLOSED"
            self._initialized = False

            logger.info("IMPORTANT! Connection to Hiven was closed! Tasks will also now be forced stopped to ensure the client stops as fast as possible and no more data transfer will happen!")

            return
        
        except Exception as e:
            logger.critical(f"Closing the connection to Hiven failed! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(e)

    async def close(self, exec_loop = True, **kwargs) -> None:
        """`openhivenpy.gateway.Connection.close()`
        
        Stops the active asyncio task that represents the connection.
        
        Paramter
        ~~~~~~~~
        
        exec_loop: `bool` - If True closes the execution_loop with the other tasks. Defaults to True
        
        """
        try:
            logger.info("Closing connection!")
            self._connection_status = "CLOSING"
            
            if kwargs.get('restart', False) == False:
                self._restart = False
                
            if not self._lifesignal.cancelled():
                self._lifesignal.cancel()
            
            if not self._connection.cancelled():
                self._connection.cancel()

            if exec_loop:                
                await self._execution_loop.stop()

            await self.http_client.close()
                
            self._connection_status = "CLOSED"
            self._initialized = False
            
            logger.info("IMPORTANT! Connection to Hiven was closed! Tasks will also now be forced stopped to ensure the client stops as fast as possible and no more data transfer will happen!")
            
            return
            
        except Exception as e:
            logger.critical(f"Closing the connection to Hiven failed! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(e)
        
    # Restarts the connection if it errored or crashed
    async def _restart_websocket(self):
        """`openhivenpy.gateway.Connection._restart_websocket()`
  
        Tries to restart when the websocket occured an error!
        
        If the restart failed again the program stops!
        
        """
        # Delaying the checks so to avoid the case that the user closes the connection 
        # and it restarts because the restart wasn't deactivated
        await asyncio.sleep(0.25)
        # var _restart from the inherited websocket
        if self._restart:
            if self.ws_connection.done():
                logger.info("Restarting was scheduled!")
                await asyncio.sleep(10)
                
                self._connection_status = "OPENING"
                
                await self.close(exec_loop=False)
            
                self.http_client = HTTPClient(loop=self._event_loop, 
                                              token=self._token, 
                                              **self._init_args)
                self.http_client.http_ready = False
                
                client_data = await self.http_client.connect()
                
                # Updating the client data based on the response
                await super().update_client_user_data(client_data['data'])
                
                logger.info("Restarting was scheduled!")
                await self.ws_connect()
        else:
            return
                
        
    