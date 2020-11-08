import asyncio
import requests
import sys
import warnings
import logging
import time
from typing import Optional

from openhivenpy.Gateway import *
from openhivenpy.Events import Events
import openhivenpy.Exception as errs
from openhivenpy.Types import Client, ClientUser

API_URL = "https://api.hiven.io"
API_VERSION = "v1"
logger = logging.getLogger(__name__)

class HivenClient(Websocket, Events, Client, API):
    """`openhivenpy.Client.HivenClient` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Main Class for connecint to Hiven and interacting with the API. 
    
    Inherits from Websocket, Events and Client
    
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
    def __init__(self, token: str, client_type: str = None, heartbeat: int = 30000, ping_timeout: int = 100, 
                 close_timeout: int = 20, ping_interval: int = None, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop()):

        if client_type == "user" or client_type == "HivenClient.UserClient":
            self._CLIENT_TYPE = "HivenClient.UserClient"
            
        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self._CLIENT_TYPE = "HivenClient.BotClient"

        elif client_type == None:
            logger.warning("Client type is None. Defaulting to BotClient. \nThis might be caused by using the HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!")
            warnings.warn("Client type is None. Defaulting to BotClient. \nThis might be caused by using the HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!", errs.NoneClientType)
            self._CLIENT_TYPE = "HivenClient.BotClient"
        
        elif client_type == "discord": #Okay i couldnt help myself.
            print("https://github.com/Rapptz/discord.py")
            return

        else:
            logger.error(f"Expected 'user' or 'bot', got '{client_type}'")
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'")

        if token == None or token == "":
            logger.critical(f"Empty Token was passed")
            raise errs.InvalidToken("Token was passed")

        elif len(token) != 128:
            logger.critical(f"Invalid Token")
            raise errs.InvalidToken("Invalid Token")

        self._CUSTOM_HEARBEAT = False if heartbeat == 30000 else True
        self._TOKEN = token
        self._event_loop = event_loop

        super().__init__(API_URL, API_VERSION, token, heartbeat, ping_timeout, close_timeout, ping_interval, event_loop)

    @property
    def token(self) -> str:
        return self._TOKEN

    async def connect(self, token=None) -> None:
        """openhivenpy.Client.HivenClient.connect()
        
        Async function for establishing a connection to Hiven. Triggers HivenClient.on_connection_start(), HivenClient.on_init() and HivenClient.on_ready()
        
        """
        asyncio.get_event_loop.run_until_complete(self.create_connection())
        return 

    def run(self) -> None:
        """openhivenpy.Client.HivenClient.run()
        
        Standard function for establishing a connection to Hiven
        
        """
        try:
            asyncio.get_event_loop.run_until_complete(self.start_event_loop())
        except RuntimeError as e:
            logger.exception(e)
            raise sys.exc_info()[0](e)

    # End User Functions #
    # Begin User Properties #

    @property
    def user(self) -> ClientUser:
        return self._USERCLIENT

    @property
    def client_type(self) -> str:
        return self._CLIENT_TYPE

    @property
    def houses(self) -> list:
        return self._HOUSES

    @property
    def users(self) -> list:
        return self._USERS

    @property
    def ping(self) -> float:
        start = time.time()
        requests.get("https://api.hiven.io/")
        if requests.status_code == 200:
            return time.time() - start
        else:
            logger.error("Trying to ping Hiven failed!")
            raise errs.ConnectionError("Unable to ping Hiven!")
        



