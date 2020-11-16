import requests
import websockets
import asyncio
import json
import time
import sys
import json
import logging
from typing import Optional

import openhivenpy.Types as types
import openhivenpy.Exception as errs
import openhivenpy.Utils as utils
from openhivenpy.Events import EventHandler

logger = logging.getLogger(__name__)

from openhivenpy.Types import Client

class API():
    """`openhivenpy.Gateway`
    
    API
    ~~~
    
    API Class for interaction with the Hiven API not depending on the HTTPClient
    
    Will soon either be repurposed or removed!
    
    
    """
    @property
    def api_url(self):
        return "https://api.hiven.io/v1"

    # Gets a json file from the hiven api
    async def get(self, keyword: str = "", headers={'content_type': 'application/json'}) -> dict:
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp

    # Sends a request to the API. Mostly so I dont have to auth 24/7.
    @staticmethod
    async def api(self, method: str, endpoint: str, token: str, body : dict): #Wish there as an easier way to auth but there isnt so..
        resp = None
        headers = {"content_type": "application/json", "authorization": token}
        if method == "get":
            resp = requests.get(f"{self.api_url}{endpoint}", headers=headers,data=body)
        elif method == "post":
            resp = requests.post(f"{self.api_url}{endpoint}", headers=headers,data=body)
        elif method == "patch":
            resp = requests.patch(f"{self.api_url}{endpoint}", headers=headers,data=body)
        elif method == "delete":
            resp = requests.delete(f"{self.api_url}{endpoint}", headers=headers,data=body)

        return resp

class Websocket(Client, API):
    """`openhivenpy.Gateway`
    
    Websocket
    ~~~~~~~~~
    
    Websocket Class that will listen to the Hiven Websocket and trigger user-specified events.
    
    Calls `openhivenpy.EventHandler` and will execute the user code if registered
    
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
    
    event_handler: 'openhivenpy.Events.EventHandler`
    
    """    
    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop(),
                 event_handler: EventHandler = EventHandler(None), **kwargs):
        
        self._API_URL = kwargs.get('api_url')
        self._API_VERSION = kwargs.get('api_version')

        self._WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self._ENCODING = "json"

        # Heartbeat is the interval where messages are going to get sent. 
        # In miliseconds
        self._HEARTBEAT = kwargs.get('heartbeat', 30000)
        self._TOKEN = kwargs.get('token', None)
        
        self._ping_timeout = kwargs.get('ping_timeout', 100)
        self._close_timeout = kwargs.get('close_timeout', 20)
        self._ping_interval = kwargs.get('ping_interval', None)
        
        self._event_handler = event_handler
        
        self._event_loop = event_loop
        
        self._CUSTOM_HEARBEAT = False if self._HEARTBEAT == 30000 else True

        super().__init__()


    @property
    def ping_timeout(self) -> int:
        return self._ping_timeout

    @property
    def close_timeout(self) -> int:
        return self._close_timeout

    @property
    def ping_interval(self) -> int:
        return self._ping_interval

    @property
    def websocket_url(self) -> str:
        return self._WEBSOCKET_URL

    @property
    def encoding(self) -> str:
        return self._ENCODING

    @property
    def heartbeat(self) -> int:
        return self._HEARTBEAT

    @property
    def websocket(self) -> websockets.client.WebSocketClientProtocol:
        return self


    # Starts the connection over a new websocket
    async def ws_connect(self, heartbeat: int or float = None) -> None:
        """
        
        Creates a connection to the Hiven API. 
        
        Not supposed to be called by the user! 
        
        Consider using HivenClient.connect() or HivenClient.run()
        
        """        

        self._HEARTBEAT = heartbeat if heartbeat != None else self._HEARTBEAT

        async def websocket_connect() -> None:
            try:
                async with websockets.connect(uri = self._WEBSOCKET_URL, ping_timeout = self._ping_timeout, 
                                              close_timeout = self._close_timeout, ping_interval = self._ping_interval) as websocket:

                    websocket = await self.ws_init(websocket)

                    # Authorizing with token
                    logger.info("Logging in with token")
                    await websocket.send(json.dumps( {"op": 2, "d": {"token": str(self._TOKEN)} } ))

                    # Receiving the first response from Hiven and setting the specified heartbeat
                    response = json.loads(await websocket.recv())
                    if response['op'] == 1 and self._CUSTOM_HEARBEAT == False:
                        self._HEARTBEAT = response['d']['hbt_int']
                        logger.debug(f"Heartbeat set to {response['d']['hbt_int']}")
                        websocket.heartbeat = self._HEARTBEAT

                    self._closed = websocket.closed
                    self._open = websocket.open

                    # Triggering the user event for the connection start
                    await self._event_handler.connection_start()

                    # Messages will be sent and received parallely
                    # => both won't block each other
                    await asyncio.gather(self.ws_lifesignal(websocket), self.ws_receive_message(websocket))

            except Exception as e:
                # Getting the place of error(line of error) 
                # and appending it to the error message

                await self.ws_on_error(e)

        # Creaing a task that wraps the courountine
        self._connection = self._event_loop.create_task(websocket_connect())
        
        # Running the task in the background
        try:
            await self._connection
        # Avoids that the user notices that the task was cancelled! aka. Silent Error
        except asyncio.CancelledError:
            logger.debug("Connection was cancelled!")
            return 
        except Exception as e:
            logger.critical(e)
            raise sys.exc_info()[0](e)
            

    # Passing values to the Websocket for more information while executing
    async def ws_init(self, ws) -> websockets.client.WebSocketClientProtocol:
        """
        
        Initialization Function for the Websocket. 
        
        Not supposed to be called by a user!
        
        """        
        ws.url = self._WEBSOCKET_URL
        ws.heartbeat = self._HEARTBEAT

        self._websocket = ws

        return ws


    # Loop for receiving messages from Hiven
    async def ws_receive_message(self, ws) -> None:
        """
        
        Handler for Receiving Messages. 
        
        Not supposed to be called by a user!
        
        """      
        try:
            while True:
                response = await ws.recv()
                if response != None:
                    logger.debug(f"Response received: {response}")
                    await self.ws_on_response(response)
        finally:
            return


    async def ws_lifesignal(self, ws) -> None:
        """
        
        Handler for Opening the Websocket. 
        
        Not supposed to be called by a user!
        
        """    
        try:
            async def start_connection():
                logger.info("Connection to Hiven established")
                self._startup_time =  time.time() - self._connection_start
                await self._event_handler.init_state(time=self._startup_time)
                
                try:
                    while self._open:
                        # Sleeping the wanted time (Pause for the Heartbeat)
                        await asyncio.sleep(self._HEARTBEAT / 1000)

                        # Lifesignal
                        await ws.send(json.dumps({"op": 3}))
                        logger.debug("Lifesignal")

                        # If the connection is closing the loop will break
                        if self._connection_status == "closing" or self._connection_status == "closed":
                            logger.info("Connection to Remote () closed!")
                            break
                finally:
                    return 

            self._connection_status = "open"

            connection = asyncio.create_task(start_connection())
            await connection

        except Exception as e:
            logger.critical(f"An error occured while trying to connect to Hiven.")
            raise errs.ConnectionError(f"An error occured while trying to connect to Hiven.\n{e}")


    # Error Handler for exceptions while running the websocket connection
    async def ws_on_error(self, error) -> None:
        """
        
        Handler for Errors in the Websocket. 
        
        Not supposed to be called by a user!
        
        """    
        try: line_of_error = sys.exc_info()[-1].tb_lineno
        except Exception as e: line_of_error = "Unknown"
        
        logger.exception(str(error).capitalize())
        raise sys.exc_info()[0](f"In Line {line_of_error}: " + str(error).capitalize())


    # Event Triggers
    async def ws_on_response(self, ctx_data) -> None:
        """
        
        Handler for the Websocket Events and the message data. 
        
        Not supposed to be called by a user!
        
        """    
        try:
            response_data = json.loads(ctx_data)
            
            logger.debug(f"Received Event {response_data['e']}")

            if response_data['e'] == "INIT_STATE":
                super().update_client_data(response_data['d'])
                await self._event_handler.ready_state(time.time())
                self._initalized = True

            elif response_data['e'] == "HOUSE_JOIN":
                
                if not hasattr(self, '_HOUSES') and not hasattr(self, '_USERS'):
                    raise errs.FaultyInitialization("The client attributes _USERS and _HOUSES do not exist! The class might be initialized faulty!")

                house = types.House(response_data['d'], self._TOKEN)
                ctx = types.Context(response_data['d'], self._TOKEN)
                await self._event_handler.house_join(ctx, house)

                for usr in response_data['d']['members']:
                    if not utils.get(self._USERS, id=usr['id'] if hasattr(usr, 'id') else usr['user']['id']):
                        # Appending to the client users list
                        self._USERS.append(types.User(usr, self._TOKEN))   
                         
                        # Appending to the house users list
                        usr = types.Member(usr, self._TOKEN)    
                        house._members.append(usr)
                
                # Appending to the client houses list
                self._HOUSES.append(house)

            elif response_data['e'] == "HOUSE_EXIT":
                house = None
                ctx = types.Context(response_data['d'], self._TOKEN)
                await self._event_handler.house_exit(ctx, house)

            elif response_data['e'] == "HOUSE_DOWN":
                logger.info(f"Downtime of {response_data['d']['name']} reported!")
                house = None #ToDo
                ctx = None
                await self._event_handler.house_down(ctx, house)

            elif response_data['e'] == "HOUSE_MEMBER_ENTER":
                ctx = types.Context(response_data['d'], self._TOKEN)
                member = types.Member(response_data['d'], self._TOKEN)
                await self._event_handler.house_member_enter(ctx, member)

            elif response_data['e'] == "HOUSE_MEMBER_EXIT":
                ctx = types.Context(response_data['d'], self._TOKEN)
                member = types.Member(response_data['d'], self._TOKEN)
                
                await self._event_handler.house_member_exit(ctx, member)

            elif response_data['e'] == "PRESENCE_UPDATE":
                precence = types.Presence(response_data['d'], self._TOKEN)
                member = types.Member(response_data['d'], self._TOKEN)
                await self._event_handler.presence_update(precence, member)

            elif response_data['e'] == "MESSAGE_CREATE":
                message = types.Message(response_data['d'], self._TOKEN)
                await self._event_handler.message_create(message)

            elif response_data['e'] == "MESSAGE_DELETE":
                message = types.Message(response_data['d'], self._TOKEN)
                await self._event_handler.message_delete(message)

            elif response_data['e'] == "MESSAGE_UPDATE":
                message = types.Message(response_data['d'], self._TOKEN)
                await self._event_handler.message_update(message)

            elif response_data['e'] == "TYPING_START":
                member = types.Typing(response_data['d'], self._TOKEN)
                await self._event_handler.typing_start(member)

            elif response_data['e'] == "TYPING_END":
                member = types.Typing(response_data['d'], self._TOKEN)
                await self._event_handler.typing_end(member)
            
            else:
                logger.debug(f"Unknown Event {response_data['e']} without Handler")
            
        except Exception as e:
            raise sys.exc_info()[0](e)
        
        return
    
