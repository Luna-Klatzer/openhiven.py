import asyncio
import requests
import sys
import logging
from time import time
from websockets import WebSocketClientProtocol
from typing import Optional
from datetime import datetime

from openhivenpy.Gateway import Connection, API
from openhivenpy.Events import EventHandler
import openhivenpy.Exception as errs
from openhivenpy.Types import Client

logger = logging.getLogger(__name__)

class HivenClient(EventHandler, API):
    """`openhivenpy.Client.HivenClient` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Main Class for connecint to Hiven and interacting with the API. 
    
    Inherits from EventHandler and API
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    client_type: `str` - Automatically set if UserClient or BotClient is used. Raises `HivenException.InvalidClientType` if set incorrectly. Defaults to `BotClient` 
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    ping_timeout: `int` - Seconds after the websocket will timeout after no succesful pong response. More information on the websockets documentation. Defaults to `100`
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake didn't complete successfully. Defaults to `20`
    
    ping_interval: `int` - Interval for sending pings to the server. Defaults to `None` because else the websocket would timeout because the Hiven Websocket does not give a response
    
    event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions. Creates a new one on default!
    
    """
    def __init__(self, token: str, client_type: str = None, 
                 event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop(), **kwargs):

        if client_type == "user" or client_type == "HivenClient.UserClient":
            self._CLIENT_TYPE = "user"
            
        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self._CLIENT_TYPE = "bot"

        elif client_type == None:
            logger.warning("Client type is None. Defaulting to BotClient. \ This might be caused by using the HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!")
            self._CLIENT_TYPE = "bot"

        else:
            logger.error(f"Expected 'user' or 'bot', got '{client_type}'")
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'")

        if token == None or token == "":
            logger.critical(f"Empty Token was passed")
            raise errs.InvalidToken("Token was passed")

        elif len(token) != 128:
            logger.critical(f"Invalid Token")
            raise errs.InvalidToken("Invalid Token")

        self._TOKEN = token
        self.loop = event_loop
        self.event_handler = EventHandler(self)
        
        # Websocket and client data are now handled over the Connection Class
        self.connection = Connection(event_handler = self.event_handler, token=token, event_loop=self.loop, **kwargs)
        
        asyncio.set_event_loop(self.loop)
        
    @property
    def token(self) -> str:
        return self._TOKEN
        
    async def connect(self) -> None:
        """openhivenpy.Client.HivenClient.connect()
        
        Async function for establishing a connection to Hiven
        
        """
        try:
            await self.connection.connect()
        except RuntimeError as e:
            logger.exception(e)
            raise sys.exc_info()[0](e)   
        finally:
            return 

    def run(self) -> None:
        """openhivenpy.Client.HivenClient.run()
        
        Standard function for establishing a connection to Hiven
        
        """
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.connection.connect())
        except RuntimeError as e:
            logger.exception(e)
            raise sys.exc_info()[0](e)   
        finally:
            return         

    # End User Functions #
    # Begin User Properties #

    @property
    def client_type(self) -> str:
        return self._CLIENT_TYPE

    @property
    def houses(self) -> list:
        return self.connection._HOUSES

    @property
    def users(self) -> list:
        return self.connection._USERS

    # Client data
    @property
    def username(self) -> str:
        return self.connection.username

    @property
    def name(self) -> str:
        return self.connection.name

    @property
    def id(self) -> int:
        return self.connection.id

    @property
    def icon(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/icons/{self._icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self._id}/headers/{self._header}"
    
    @property
    def bot(self) -> bool:
        return self.connection.bot

    @property
    def location(self) -> str:
        return self.connection.location

    @property
    def website(self) -> str:
        return self.connection.website

    @property
    def joined_at(self) -> datetime:
        return self.connection.joined_at

    @property
    def presence(self):
        return self.connection.presence

    @property
    def ping(self) -> float:
        start = time()
        res = requests.get("https://api.hiven.io/")
        if res.status_code == 200:
            return time() - start
        else:
            logger.warning("Trying to ping Hiven failed!")
            return None
        
    @property
    def connection_possible(self) -> bool:
        """openhivenpy.Client.HivenClient.connection_possible()
        
        Checks whetever the connection to Hiven is alive and possible!
        
        Alias for ping() but returns either True or False based on the response status code.
        
        """
        res = requests.get("https://api.hiven.io/")
        if res.status_code == 200:
            return True
        else:
            logger.warning("Trying to ping Hiven failed!")
            return False        
        
    async def stop(self):
        """
        
        Kills the event loop and the running tasks! 
        
        Will likely throw a RuntimeError if the Client was started in a courountine or if future courountines are going to get executed!
        
        """
        await self.connection.stop_event_loop()
        
    async def close(self):        
        """
        
        Stops the active asyncio task that represents the connection.
        
        """
        await self.connection.close()
        return

    # Websocket Properties
    @property
    def connection_status(self) -> str:
        return self.connection.connection_status
    
    @property
    def heartbeat(self) -> str:
        return self.connection.heartbeat
    
    @property
    def get_connection_status(self) -> str:
        return self.connection.get_connection_status
    
    @property
    def open(self) -> bool:
        return self.connection.open
    
    @property
    def closed(self) -> bool:
        return self.connection.closed

    @property
    def websocket(self) -> WebSocketClientProtocol:
        """
        
        Returns the ReadOnly Websocket with it's configuration
        
        """    
        return self.ws.websocket
    
    @property
    def initalized(self) -> bool:
        return self.connection.initalized
    
    @property
    def connection_start(self) -> float:
        return self.connection.connection_start
    
    @property
    def startup_time(self) -> float:
        return self.connection.startup_time
