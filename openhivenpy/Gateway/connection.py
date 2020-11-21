import asyncio
import logging
import sys
import time
from functools import wraps

from openhivenpy.Types import HivenClient
from openhivenpy.Events import EventHandler
from . import Websocket, HTTPClient

logger = logging.getLogger(__name__)

def get_args(**kwargs):
    return {
        "api_url": kwargs.get('api_url', "https://api.hiven.io"),
        "api_version": kwargs.get('api_version', "v1"),
        "heartbeat": kwargs.get('heartbeat', 30000),
        "ping_timeout": kwargs.get('ping_timeout', 100),
        "close_timeout": kwargs.get('close_timeout', 20),
        "ping_interval": kwargs.get('ping_interval', None),
        "event_loop": kwargs.get('event_loop')
    }


class ExecutionLoop():
    """`openhivenpy.Gateway.ConnectionLoop` 
    
    ExecutionLoop
    ~~~~~~~~~~~~~
    
    Loop that executs tasks in the background.
    
    Not yet ready for users
    
    Parameter:
    ----------
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    """
    
    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.event_loop = event_loop
        self.tasks = []
        self.startup_tasks = []
        self.startup_methods = self.StartupTasks()
        
    class StartupTasks:
        pass
        
    async def start_loop(self) -> None:
        """`openhivenpy.Gateway.ConnectionLoop.stop_loop` 
        
        Starts the current execution_loop
        
        """
        try:
            async def execute_loop(tasks) -> None:
                try:
                    if not self.startup_tasks == []:
                        methods_to_call = []
                        for task in self.startup_tasks:
                            task = getattr(self.startup_methods, task)
                            methods_to_call.append(self.event_loop.create_task(task()))
                            
                        await asyncio.gather(*methods_to_call, loop=self.event_loop)
                    
                    if not self.tasks == []:
                        while True:
                            methods_to_call = []
                            for task in self.tasks:
                                methods_to_call.append(self.event_loop.create_task(getattr(self, task)()))
                            
                            await asyncio.gather(*methods_to_call, loop=self.event_loop)
                        
                except Exception as e:
                    raise sys.exc_info()[0](e)
                finally:
                    return
                
            loop = self.event_loop.create_task(execute_loop(self.tasks))
            await loop
            
        except asyncio.CancelledError:
            logger.debug("Connection was cancelled!")
            return 

    async def stop_loop(self) -> None:
        """`openhivenpy.Gateway.ConnectionLoop.stop_loop` 
        
        Stops the current execution_loop
        
        """
        try:
            if not self.execution_loop.cancelled():
                self.execution_loop.cancel()
            return
            
        except Exception as e:
            logger.critical(f"An error occured while trying to stopping the execution loop: {e}")
            raise sys.exc_info()[0](e)
        
    def create_task(self, func=None):
        """`openhivenpy.Gateway.ConnectionLoop.create_task` 
        
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
            self.one_time_tasks.append(func.__name__)
            
            logger.debug(f"Taks {func.__name__} added to loop")

            return func # returning func means func can still be used normally

        if func == None:    
            return decorator
        else:
            return decorator(func)
    
    def create_one_time_task(self, func=None):
        """`openhivenpy.Gateway.ConnectionLoop.create_task` 
        
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
            
            setattr(self.startup_methods, func.__name__, wrapper)
            self.startup_tasks.append(func.__name__)
            
            logger.debug(f"Startup Taks {func.__name__} added to loop")

            return func # returning func means func can still be used normally

        if func == None:    
            return decorator
        else:
            return decorator(func)


class Connection(Websocket, HivenClient):
    """`openhivenpy.Gateway.Connection` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Class that wraps the Websocket, HTTPClient and the Data in the current connection to one class.
    
    Inherits from Websocket, HivenClient
    
    Parameter:
    ----------
    
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
        self._initalized = False
        self._connection_start = None
        
        self._connection_status = "closed"
        
        args = get_args(**kwargs)
        self._API_URL = args.get('api_url')
        self._API_VERSION = args.get('api_version')

        self._event_loop = args.get('event_loop')
        self._execution_loop = ExecutionLoop(self._event_loop)
        
        self.http_client = HTTPClient(loop=self._event_loop, token=token, **args)
        self.http_client.http_ready = False
        
        super().__init__(event_handler=event_handler, token=token, **args)

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
        return self._initalized

    @property
    def connection_start(self) -> float:
        return self._connection_start

    @property
    def startup_time(self) -> float:
        return self._startup_time
    
    async def connect(self) -> None:
        """`openhivenpy.Gateway.Connection.connect()`

        Establishes a connection to Hiven
        
        """
        try:
            # Connection Start variable for later calculation the time how long it took to start
            self._connection_start = time.time()
            self._connection_status = "opening"
            
            # Starting the HTTPClient Connection to Hiven
            client_data = await self.http_client.connect()
            self.http_client.http_ready = True
            
            await super().update_client_user_data(client_data['data'])
            
            # Starting the event loop with the websocket
            await asyncio.gather(self.ws_connect(), self._execution_loop.start_loop())
            
        finally:
            self._connection_status = "closed"    
            return
        
        
    # Kills the connection as well as the event loop
    async def destroy(self) -> None:
        """`openhivenpy.Gateway.Connection.destroy()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw `RuntimeError` if the HivenClient was started in a courountine or if future courountines are going to get executed!
        
        """
        
        try:
            logger.info(f"Connection to the Hiven Websocket closed!")
            self._connection_status = "closing"
            
            if not self._connection.cancelled():
                self._connection.cancel()
            
            await self._event_loop.shutdown_asyncgens()
            self._event_loop.stop()
            self._event_loop.close()
            
            self._connection_status = "closed"

        except Exception as e:
            logger.critical(f"Error while trying to close the connection{e}")
            raise sys.exc_info()[0](e)
        
        return

    async def close(self) -> None:
        """`openhivenpy.Gateway.Connection.close()`
        
        Stops the active asyncio task that represents the connection.
        
        """
        try:
            logger.info(f"Connection to the Hiven Websocket closed!")
            self._connection_status = "closing"
            
            if not self._connection.cancelled():
                self._connection.cancel()
                
            self._connection_status = "closed"
            self.initalized = False
            
        except Exception as e:
            logger.critical(f"An error occured while trying to close the connection to Hiven: {e}")
            raise sys.exc_info()[0](e)
    