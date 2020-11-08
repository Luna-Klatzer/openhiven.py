import asyncio
import requests
import sys
import warnings
import logging

from openhivenpy.Websocket import Websocket
from openhivenpy.Events import Events
import openhivenpy.Exception as errs
from openhivenpy.Types import Client, ClientUser

API_URL = "https://api.hiven.io"
API_VERSION = "v1"
logger = logging.getLogger(__name__)

class HivenClient(Websocket, Events, Client):
    """`openhivenpy.Client.HivenClient` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Main Class for connecint to Hiven and interacting with the API. 
    
    Inherits from Websocket, Events and Client
    
    """
    def __init__(self, token: str, client_type: str = None,  heartbeat: int = 30000, ping_timeout: int = 100, 
                 close_timeout: int = 20, ping_interval: int = None):

        if client_type == "user" or client_type == "HivenClient.UserClient":
            self._CLIENT_TYPE = "HivenClient.UserClient"
            
        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self._CLIENT_TYPE = "HivenClient.BotClient"

        elif client_type == None:
            logger.warning("Client type is None. Defaulting to BotClient. \nThis might be caused by using the HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!")
            warnings.warn("Client type is None. Defaulting to BotClient. \nThis might be caused by using the HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!", errs.NoneClientType)
            self._CLIENT_TYPE = "HivenClient.BotClient"

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

        super().__init__(API_URL, API_VERSION, token, heartbeat, ping_timeout, close_timeout, ping_interval)

    async def connect(self, token=None) -> None:
        """openhivenpy.Client.HivenClient.connect()
        
        Async function for establishing a connection to Hiven. Triggers HivenClient.on_connection_start(), HivenClient.on_init() and HivenClient.on_ready()
        
        """
        await self.create_connection()
        return 

    def run(self) -> None:
        """openhivenpy.Client.HivenClient.run()
        
        Standard function for establishing a connection to Hiven. Triggers on_connection_start(), on_init() and on_ready()
        
        """
        asyncio.run(self.start_event_loop())

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

        



