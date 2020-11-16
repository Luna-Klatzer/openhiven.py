import asyncio
import logging
import sys
import time

from openhivenpy.Types import Client
from openhivenpy.Events import EventHandler
from . import API, Websocket, HTTPClient

logger = logging.getLogger(__name__)

def get_args(**kwargs):
    args = {
        "api_url": kwargs.get('api_url', "https://api.hiven.io"),
        "api_version": kwargs.get('api_version', "v1"),
        "token": kwargs.get('token', None),
        "heartbeat": kwargs.get('heartbeat', 30000),
        "ping_timeout": kwargs.get('ping_timeout', 100),
        "close_timeout": kwargs.get('close_timeout', 20),
        "ping_interval": kwargs.get('ping_interval', None),
        "event_loop": kwargs.get('event_loop')
    }
    return args

class Connection(Websocket, Client):
    """`openhivenpy.Gateway.Connection` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Class that wraps the Websocket, HTTPClient and the Data in the current connection to one class.
    
    Inherits from Websocket, Client
    
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
    def __init__(self, event_handler: EventHandler, **kwargs):
        
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
        
        self.http_client = HTTPClient(loop=self._event_loop, **args)
        
        super().__init__(event_handler=event_handler, **args)

    async def connect(self) -> None:
        """`openhivenpy.Gateway.Connection.connect()`

        Establishes a connection to Hiven
        
        """
        try:
            # Connection Start variable for later calculation the time how long it took to start
            self._connection_start = time.time()
            
            client_data = await self.http_client.connect()
            self.http_client.http_ready = True
            
            print(await self.http_client.request(endpoint="/users/@me"))
            
            super().update_client_data(client_data['data'])
            await self.ws_connect()
        finally:
            return
        
        
    # Kills the connection as well as the event loop
    async def destroy(self) -> None:
        """`openhivenpy.Gateway.Connection.destroy()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw `RuntimeError` if the Client was started in a courountine or if future courountines are going to get executed!
        
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
    def get_connection_status(self) -> str:
        return self.connection_status

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
    