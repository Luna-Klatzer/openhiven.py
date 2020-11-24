import asyncio
import requests
import sys
import logging
import nest_asyncio
from time import time
from websockets import WebSocketClientProtocol
from typing import Optional
from datetime import datetime

from openhivenpy.gateway import Connection, API
from openhivenpy.events import EventHandler
import openhivenpy.exceptions as errs
import openhivenpy.utils as utils
from openhivenpy.types import Room, House, User

logger = logging.getLogger(__name__)

def _check_dependencies() -> None:
    pkgs = ['asyncio', 'requests', 'websockets', 'typing', 'nest_asyncio', 'aiohttp']
    for pkg in pkgs:
        if pkg not in sys.modules:
            logger.critical(f"Module {pkg} not found in locally installed modules!")
            raise ImportError(f"Module {pkg} not found in locally installed modules!", name=pkg)

class HivenClient(EventHandler, API):
    """`openhivenpy.client.HivenClient` 
    
    HivenClient
    ~~~~~~~~~~~
    
    Main Class for connecint to Hiven and interacting with the API. 
    
    Inherits from EventHandler and API
    
    Parameter:
    ----------
    
    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    restart: `bool` - If set to True the process will restart if Error Code 1011 or 1006 is thrown
    
    client_type: `str` - Automatically set if UserClient or BotClient is used. Raises `HivenException.InvalidClientType` if set incorrectly. Defaults to `BotClient` 
    
    event_handler: `openhivenpy.events.EventHandler` - Handler for the events. Can be modified and customized if wanted. Creates a new one on Default
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    ping_timeout: `int` - Seconds after the websocket will timeout after no succesful pong response. More information on the websockets documentation. Defaults to `100`
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake didn't complete successfully. Defaults to `20`
    
    ping_interval: `int` - Interval for sending pings to the server. Defaults to `None` because else the websocket would timeout because the Hiven Websocket does not give a response
    
    event_loop: Optional[`asyncio.AbstractEventLoop`] - Event loop that will be used to execute all async functions. Creates a new one on default
    
    """
    def __init__(self, token: str, *, client_type: str = None, event_handler: EventHandler = None,
                 event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(), **kwargs):

        if client_type == "user" or client_type == "HivenClient.UserClient":
            self._CLIENT_TYPE = "user"
            self._is_bot = False
            
        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self._CLIENT_TYPE = "bot"
            self._is_bot = True

        elif client_type == None:
            logger.warning("client type is None. Defaulting to BotClient. This might be caused by using the HivenClient Class directly which can cause exceptions when using BotClient or UserClient Functions!")
            self._CLIENT_TYPE = "bot"
            self._is_bot = True

        else:
            logger.error(f"Expected 'user' or 'bot', got '{client_type}'")
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'")

        if token == None or token == "":
            logger.critical(f"Empty Token was passed!")
            raise errs.InvalidToken

        elif len(token) != 128:
            logger.critical(f"Invalid Token was passed!")
            raise errs.InvalidToken

        _check_dependencies()

        self._TOKEN = token
        self.loop = event_loop
        self.event_handler = EventHandler(self) if event_handler == None else event_handler
        
        # Websocket and client data are being handled over the Connection Class
        self.connection = Connection(event_handler=self.event_handler, 
                                     token=token, 
                                     event_loop=self.loop, 
                                     **kwargs)
        
        # Not sure if that's a good solution to the issue but I will do this
        nest_asyncio.apply(loop=self.loop)
    
    @property
    def token(self) -> str:
        return self._TOKEN
        
    async def connect(self) -> None:
        """`openhivenpy.client.HivenClient.connect()`
        
        Async function for establishing a connection to Hiven
        
        """
        try:
            self.loop.run_until_complete(self.connection.connect())
        except RuntimeError as e:
            logger.exception(e)
            raise errs.ConnectionError(f"Failed to start client session and websocket! Cause of Error: {e}")   
        finally:
            return 

    def run(self) -> None:
        """`openhivenpy.client.HivenClient.run()`
        
        Standard function for establishing a connection to Hiven
        
        """
        try:
            self.loop.run_until_complete(self.connection.connect())
        except RuntimeError as e:
            logger.exception(e)
            raise errs.ConnectionError(f"Failed to start session and establish connection to Hiven! Cause of Error: {e}")   
        finally:
            return         

    async def stop(self):
        """`openhivenpy.HivenClient.stop()`
        
        Kills the event loop and the running tasks! 
        
        Will likely throw a RuntimeError if the client was started in a courountine or if future courountines are going to get executed!
        
        """
        try:
            if self.connection.closed:
                await self.connection.stop_event_loop()
                return True
            else:
                logger.error("An attempt to close the connection to Hiven failed due to no current active Connection!")
                return False
        except Exception as e:
            logger.error(f"Failed to close client session and websocket to Hiven! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to close client session and websocket to Hiven! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
    async def close(self) -> bool:        
        """`openhivenpy.HivenClient.close()`
        
        Stops the active asyncio task that represents the connection.
        
        Returns `True` if successful
        
        """
        try:
            if self.connection.closed:
                await self.connection.close()
                return True
            else:
                logger.error("An attempt to close the connection to Hiven failed due to no current active Connection!")
                return False
        except Exception as e:
            logger.error(f"Failed to close client session and websocket to Hiven! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.UnableToClose(f"Failed to close client session and websocket to Hiven! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    @property
    def client_type(self) -> str:
        return self._CLIENT_TYPE

    # Meta data
    # -----------
    @property
    def amount_houses(self) -> list:
        return self.connection._amount_houses
    
    @property
    def houses(self) -> list:
        return self.connection._houses

    @property
    def users(self) -> list:
        return self.connection._users

    @property
    def rooms(self) -> list:
        return self.connection._rooms

    @property
    def private_rooms(self) -> list:
        return self.connection._private_rooms

    @property
    def relationships(self) -> list:
        return self.connection._relationships

    # Client data
    # -----------
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
        return f"https://media.hiven.io/v1/users/{self.id}/icons/{self.connection.icon}"

    @property
    def header(self) -> str:
        return f"https://media.hiven.io/v1/users/{self.id}/headers/{self.connection.header}"
    
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
        """`openhivenpy.client.HivenClient.ping`
        
        Returns the current ping of the HTTPClient.
        
        """
        if self.connection.http_client.http_ready:
            start = time()
            res = asyncio.run(self.connection.http_client.raw_request("/users/@me", method="get"))
            if res.status == 200:
                return time() - start
            else:
                logger.warning("Trying to ping Hiven failed!")
                return None
        else:
            return None
        
    @property
    def connection_possible(self) -> bool:
        """`openhivenpy.client.HivenClient.connection_possible()`
        
        Checks whetever the connection to Hiven is alive and possible!
        
        Alias for ping() but does not need the client to be connected!
        
        """
        res = requests.get("https://api.hiven.io/")
        if res.status_code == 200:
            return True
        else:
            logger.warning("The attempt to ping Hiven failed!")
            return False        

    async def edit(self, data: str, value: str) -> bool:
        """`openhivenpy.HivenClient.edit()`
        
        Change the signed in user's/bot's data. 
        
        Available options: header, icon, bio, location, website.
        
        Alias for hivenclient.connection.edit()
        
        """
        if self.connection.http_client.http_ready:
            return await self.connection.edit(data=data, value=value)
        else:
            logging.error("HTTPClient Request was attempted without active Connection!")
            raise errs.ConnectionError("HTTPClient Request was attempted without active Connection!")
            return None

    async def getRoom(self, id: float) -> Room:
        """`openhivenpy.HivenClient.getRoom()`
        
        Returns a cached Hiven Room Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_room()
        
        """
        return utils.get(self.rooms, id=id)

    async def getHouse(self, id: float) -> Room:
        """`openhivenpy.HivenClient.getHouse()`
        
        Returns a cached Hiven Room Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_house()
        
        """
        return utils.get(self.houses, id=id)

    async def getUser(self, id: float) -> Room:
        """`openhivenpy.HivenClient.getUser()`
        
        Returns a cached Hiven User Object
        
        Warning:
        --------
        
        Data can and will probably be outdated!
        
        Only use this when up-to-date data does not matter or only small checks need to be made on the Room!
        
        Rather consider using get_user()
    
        """
        return utils.get(self.users, id=id)
        
    async def get_house(self, house_id: float) -> House:
        """`openhivenpy.HivenClient.get_house()`
        
        Returns a Hiven House Object based on the passed id.
        
        Returns the House if it exists else returns None
        
        """
        cached_house = utils.get(self.houses, id=house_id)
        if cached_house != None:
            return cached_house
        
            # Not yet possible
            data = await self.connection.http_client.request(endpoint=f"/houses/{id}")
            house = House(data['d'], self.connection.http_client, self.id)
            if cached_house:
                self.connection._houses.remove(cached_house)
            self.connection._houses.append(house)
            return house
        return None
            
    async def get_user(self, user_id: float) -> User:
        """`openhivenpy.HivenClient.get_user()`
        
        Returns a Hiven User Object based on the passed id.
        
        Returns the House if it exists else returns None
        
        """
        cached_user = utils.get(self.users, id=user_id)
        if cached_user != None:
            data = await self.connection.http_client.request(endpoint=f"/users/{id}")
            user = User(data['d'], self.connection.http_client)
            if cached_user:
                self.connection._houses.remove(cached_user)
            self.connection._houses.append(user)
            return user
        return None
      
    async def get_room(self, room_id: float) -> Room:
        """`openhivenpy.HivenClient.get_room()`
        
        Returns a Hiven Room Object based on the passed house id and room id.
        
        Returns the Room if it exists else returns None
        
        """
        cached_room = utils.get(self.rooms, id=room_id)
        if cached_room != None:
            data = await self.connection.http_client.request(endpoint=f"/rooms/{room_id}")
            room = Room(data['d'], self.connection.http_client)
            if cached_room:
                self.connection._houses.remove(cached_room)
            self.connection._houses.append(room)
            return room
        return None
            

    # General Connection Properties    
    @property
    def heartbeat(self) -> str:
        return self.connection.heartbeat
    
    @property
    def connection_status(self) -> str:
        """`openhivenpy.HivenClient.get_connection_status`

        Returns a string with the current connection status.
        
        Can be either 'opening', 'open', 'closing' or 'closed'

        """
        return self.connection.connection_status
    
    @property
    def open(self) -> bool:
        """`openhivenpy.HivenClient.websocket`
        
        Returns `True` if the connection is open
        
        Opposite property to closed
        
        """  
        return self.connection.open
    
    @property
    def closed(self) -> bool:
        """`openhivenpy.HivenClient.closed`

        Returns `True` if the connection is closed
        
        Opposite property to open
        
        """
        return self.connection.closed

    @property
    def websocket(self) -> WebSocketClientProtocol:
        """`openhivenpy.HivenClient.websocket`
        
        Returns the ReadOnly Websocket with it's configuration
        
        """    
        return self.connection.websocket
    
    @property
    def initalized(self) -> bool:
        """`openhivenpy.HivenClient.initalized`

        True if Websocket and HTTPClient are connected and running
        
        """
        return self.connection.initalized
    
    @property
    def connection_start(self) -> float:
        """`openhivenpy.HivenClient.connection_start`

        Point of connection start in unix dateformat
        
        """
        return self.connection.connection_start
    
    @property
    def startup_time(self) -> float:
        return self.connection.startup_time
