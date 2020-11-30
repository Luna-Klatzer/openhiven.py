import requests
import websockets
import asyncio
import json
import time
import sys
import json
import logging
from typing import Optional

import openhivenpy.types as types
import openhivenpy.exceptions as errs
import openhivenpy.utils as utils
from openhivenpy.events import EventHandler
from openhivenpy.types import Client

__all__ = ('API', 'Websocket')

logger = logging.getLogger(__name__)

class API():
    """`openhivenpy.gateway`
    
    API
    ~~~
    
    API Class for interaction with the Hiven API not depending on the HTTPClient
    
    Will soon either be repurposed or removed!
    
    """
    @property
    def host(self):
        return "https://api.hiven.io/v1"

    # Gets a json file from the hiven api
    async def get(self, keyword: str = "", headers={'content_type': 'application/json'}) -> dict:
        resp = requests.get(url=f"{self.host}/{keyword}")
        return resp

    # Sends a request to the API. Mostly so I dont have to auth 24/7.
    @staticmethod
    async def api(self, method: str, endpoint: str, token: str, body : dict): #Wish there as an easier way to auth but there isnt so..
        resp = None
        headers = {"content_type": "application/json", "authorization": token}
        if method == "get":
            resp = requests.get(f"{self.host}{endpoint}", headers=headers,data=body)
        elif method == "post":
            resp = requests.post(f"{self.host}{endpoint}", headers=headers,data=body)
        elif method == "patch":
            resp = requests.patch(f"{self.host}{endpoint}", headers=headers,data=body)
        elif method == "delete":
            resp = requests.delete(f"{self.host}{endpoint}", headers=headers,data=body)

        return resp

class Websocket(Client, API):
    """`openhivenpy.gateway.Websocket`
    
    Websocket
    ~~~~~~~~~
    
    Websocket Class that will listen to the Hiven Websocket and trigger user-specified events.
    
    Calls `openhivenpy.EventHandler` and will execute the user code if registered
    
    Is directly inherited into connection and cannot be used as a standalone class!
    
    Parameter:
    ----------
    
    restart: `bool` - If set to True the process will restart if Error Code 1011 or 1006 is thrown
    
    host: `str` - Url for the API which will be used to interact with Hiven. Defaults to 'api.hiven.io' 
    
    api_version: `str` - Version string for the API Version. Defaults to 'v1' 
    
    token: `str` - Needed for the authorization to Hiven. Will throw `HivenException.InvalidToken` if length not 128, is None or is empty
    
    heartbeat: `int` - Intervals in which the bot will send life signals to the Websocket. Defaults to `30000`
    
    ping_timeout: `int` - Seconds after the websocket will timeout after no successful pong response. More information on the websockets documentation. Defaults to `100`
    
    close_timeout: `int` -  Seconds after the websocket will timeout after the end handshake didn't complete successfully. Defaults to `20`
    
    ping_interval: `int` - Interval for sending pings to the server. Defaults to `None` because else the websocket would timeout because the Hiven Websocket does not give a response
    
    event_loop: `asyncio.AbstractEventLoop` - Event loop that will be used to execute all async functions.
    
    event_handler: 'openhivenpy.events.EventHandler` - Handler for Websocket Events
    
    """    
    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = asyncio.new_event_loop(),
                 event_handler: EventHandler = EventHandler(None), **kwargs):
        
        self._HOST = kwargs.get('api_url', 'api.hiven.io')
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
        
        self._restart = kwargs.get('restart', False)
        self._log_ws_output = kwargs.get('log_ws_output', False)
        
        self._CUSTOM_HEARBEAT = False if self._HEARTBEAT == 30000 else True

        # client data is inherited here and will be then passed to the connection class
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

    @property
    def ws_connection(self) -> asyncio.Task:
        return self._connection

    # Starts the connection over a new websocket
    async def ws_connect(self, heartbeat: int = None) -> None:
        """`openhivenpy.gateway.Websocket.ws_connect()`
        
        Creates a connection to the Hiven API. 
        
        Not supposed to be called by the user! 
        
        Consider using HivenClient.connect() or HivenClient.run()
        
        """        
        self._HEARTBEAT = heartbeat if heartbeat != None else self._HEARTBEAT

        async def websocket_connect() -> None:
            try:
                async with websockets.connect(
                                            uri = self._WEBSOCKET_URL, 
                                            ping_timeout = self._ping_timeout, 
                                            close_timeout = self._close_timeout,
                                            ping_interval = self._ping_interval) as ws:

                    ws = await self.ws_init(ws)

                    # Authorizing with token
                    logger.info("[WEBSOCKET] >> Logging in with token")
                    await ws.send(json.dumps( {"op": 2, "d": {"token": str(self._TOKEN)} } ))

                    # Receiving the first response from Hiven and setting the specified heartbeat
                    resp = json.loads(await ws.recv())
                    
                    if resp['op'] == 1 and self._CUSTOM_HEARBEAT == False:
                        self._HEARTBEAT = resp['d']['hbt_int']
                        ws.heartbeat = self._HEARTBEAT

                    logger.debug(f"[WEBSOCKET] >> Heartbeat set to {ws.heartbeat}")

                    self._closed = ws.closed
                    self._open = ws.open

                    self._connection_status = "OPEN"    

                    # Triggering the user event for the connection start
                    await self._event_handler.connection_start()
                    
                    await asyncio.gather(self.ws_lifesignal(ws), self.ws_receive_response(ws))
   
            except websockets.exceptions.ConnectionClosedOK as e:
                logger.critical(f"[WEBSOCKET] << Connection was closed! Reason: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
                stop_loop = True if self._restart == False else False 
                await self.close(exec_loop=stop_loop, restart=self._restart) # Closing and restarting the running connection!
            
            except websockets.exceptions.ConnectionClosedError as e:
                logger.critical(f"[WEBSOCKET] << Connection died abnormally! Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
                raise errs.WSConnectionError(f"[WEBSOCKET] << An error occured while trying to connect to Hiven. Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            
            except Exception as e:
                await self.ws_on_error(e)
            finally:
                return

        # Creaing a task that wraps the courountine
        self._connection = self._event_loop.create_task(websocket_connect())
        
        # Running the task in the background
        try:
            await self._connection
        # Avoids that the user notices that the task was cancelled! aka. Silent Error
        except asyncio.CancelledError:
            logger.debug("[WEBSOCKET] << The webocket Connection to Hiven unexpectedly stopped! Probably caused by an error or automatic/forced closing!") 
        except Exception as e:
            logger.critical(e)
            raise errs.GatewayException(f"[WEBSOCKET] << Exception in main-websocket process! Cause of error{sys.exc_info()[1].__class__.__name__}, {str(e)}")
        finally:
            return
            
            
    # Passing values to the Websocket for more information while executing
    async def ws_init(self, ws) -> websockets.client.WebSocketClientProtocol:
        """`openhivenpy.gateway.Websocket.ws_init()`
        
        Initialization Function for the Websocket. 
        
        Not supposed to be called by a user!
        
        """        
        ws.url = self._WEBSOCKET_URL
        ws.heartbeat = self._HEARTBEAT

        self._websocket = ws

        return ws


    # Loop for receiving messages from Hiven
    async def ws_receive_response(self, ws) -> None:
        """`openhivenpy.gateway.Websocket.ws_receive_response()`
        
        Handler for Receiving Messages. 
        
        Not supposed to be called by a user!
        
        """      
        while True:
            resp = await ws.recv()
            if resp != None:
                if self._log_ws_output:
                    logger.debug(f"[WEBSOCKET] << Response received: {resp}")
                await self.ws_on_response(resp)

    async def ws_lifesignal(self, ws) -> None:
        """`openhivenpy.gateway.Websocket.ws_lifesignal()`
        
        Handler for Opening the Websocket. 
        
        Not supposed to be called by a user!
        
        """    
        try:
            async def _lifesignal():
                logger.info("[WEBSOCKET] << Connection to Hiven established")
                while self._open:
                    # Sleeping the wanted time (Pause for the Heartbeat)
                    await asyncio.sleep(self._HEARTBEAT / 1000)

                    # Lifesignal
                    await ws.send(json.dumps({"op": 3}))
                    logger.debug("[WEBSOCKET] >> Lifesignal")

                    # If the connection is CLOSING the loop will break
                    if self._connection_status == "CLOSING" or self._connection_status == "CLOSED":
                        logger.info(f"[WEBSOCKET] << Connection to Remote ({self._WEBSOCKET_URL}) closed!")
                        break

            self._connection_status = "OPEN"

            self._lifesignal = asyncio.create_task(_lifesignal())
            await self._lifesignal
            
        except asyncio.CancelledError as e:
            logger.debug(f"[WEBSOCKET] >> Lifesignal task stopped unexpectedly! Probably caused by an error or automatic/forced closing!") 
            return
            
        except websockets.exceptions.ConnectionClosedError as e:
            logger.critical(f"[WEBSOCKET] >> Connection died abnormally! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.WSConnectionError("Connection died abnormally! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

        except Exception as e:
            logger.critical(f"[WEBSOCKET] >> The connection to Hiven failed to be kept alive or started! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
            raise errs.WSConnectionError(f"The connection to Hiven failed to be kept alive or started! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")


    # Error Handler for exceptions while running the websocket connection
    async def ws_on_error(self, e):
        """`openhivenpy.gateway.Websocket.ws_on_error()`
        
        Handler for Errors in the Websocket. 
        
        Not supposed to be called by a user!
        
        """      
        logger.critical(f"[WEBSOCKET] >> The connection to Hiven failed to be kept alive or started! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        raise errs.WSConnectionError(f"The connection to Hiven failed to be kept alive or started! Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")

    # Event Triggers
    async def ws_on_response(self, ctx_data):
        """`openhivenpy.gateway.Websocket.ws_on_response()`

        Handler for the Websocket events and the message data. 

        Not supposed to be called by a user!
        
        """
        try:
            resp = json.loads(ctx_data)
            response_data = resp.get('d', {})
            
            logger.debug(f"Received Event {resp['e']}")

            if not hasattr(self, '_houses') and not hasattr(self, '_users'):
                logger.error("[WEBSOCKET] << The client attributes _users and _houses do not exist! The class might be initialized faulty!")
                raise errs.FaultyInitialization("The client attributes _users and _houses do not exist! The class might be initialized faulty!")

            if resp['e'] == "INIT_STATE":
                await super().update_client_user_data(response_data)
                
                init_time = time.time() - self._connection_start
                await self._event_handler.init_state(time=init_time)
                self._initialized = True

            elif resp['e'] == "HOUSE_JOIN":
                house = types.House(response_data, self.http_client, super().id)
                ctx = types.Context(response_data, self.http_client)
                await self._event_handler.house_join(ctx, house)

                for usr in response_data['members']:
                    user = utils.get(self._users, id=usr['id'] if hasattr(usr, 'id') else usr['user']['id'])
                    if user == None:
                        # Appending to the client users list
                        self._users.append(types.User(usr, self.http_client))   
                         
                        # Appending to the house users list
                        usr = types.Member(usr, self._TOKEN, house)    
                        house._members.append(usr)

                for room in response_data.get('rooms'):
                    self._rooms.append(types.Room(room, self.http_client, house))
                
                # Appending to the client houses list
                self._houses.append(house)

            elif resp['e'] == "HOUSE_EXIT":
                house = None
                ctx = types.Context(response_data, self.http_client)
                await self._event_handler.house_exit(house)

            elif resp['e'] == "HOUSE_DOWN":
                t = time.time()
                house = utils.get(self._houses, id=int(response_data.get('house_id')))
                logger.info(f"[WEBSOCKET] << Downtime of '{house.name}' reported! House was either deleted or is currently unavailable!")
                await self._event_handler.house_down(t, house)

            elif resp['e'] == "HOUSE_MEMBER_ENTER":
                if self._ready:
                    ctx = types.Context(response_data, self.http_client)
             
                    house_id = response_data.get('house_id')
                    if house_id == None:
                        house_id = response_data.get('house', {}).get('id')       
                    house = utils.get(self._houses, id=int(house_id))
                    
                    # Removing the old user and appending the new data so it's up-to-date
                    user_id = response_data.get('user_id')
                    if user_id == None:
                        user_id = response_data.get('user', {}).get('id')
                    cached_user = utils.get(self._users, id=int(user_id))
                    if response_data.get('user') != None:
                        user = types.User(response_data['user'], self.http_client)
                        
                        if cached_user:
                            self._users.remove(cached_user)
                        self._users.append(user)
                    else:
                        user = cached_user
                    
                    # Removing the old member and appending the new data so it's up-to-date
                    cached_member = utils.get(house._members, user_id=int(response_data.get('user_id')))
                    if response_data.get('user') != None:
                        member = types.Member(response_data['user'], self.http_client, house)
                        
                        if cached_member:
                            house._members.remove(cached_member)
                        house._members.append(member)
                    else:
                        member = cached_user        
                    
                    await self._event_handler.house_member_enter(member, house)

            elif resp['e'] == "HOUSE_MEMBER_UPDATE":
                if self._ready:
                    house = utils.get(self._houses, id=int(response_data.get('house_id')))
                    
                    # Removing the old user and appending the new data so it's up-to-date
                    cached_user = utils.get(self._users, id=int(response_data.get('user_id')))
                    if response_data.get('user') != None:
                        user = types.User(response_data['user'], self.http_client)
                        
                        if cached_user:
                            self._users.remove(cached_user)
                        self._users.append(user)
                    else:
                        user = cached_user

                    # Removing the old member and appending the new data so it's up-to-date
                    cached_member = utils.get(house._members, user_id=int(response_data.get('user_id')))
                    if response_data.get('user') != None:
                        member = types.Member(response_data['user'], self.http_client, house)
                        
                        if cached_member:
                            house._members.remove(cached_member)
                        house._members.append(member)
                    else:
                        member = cached_user             

                    await self._event_handler.house_member_update(member, house)
                
            elif resp['e'] == "HOUSE_MEMBER_EXIT":
                ctx = types.Context(response_data, self.http_client)
                user = types.User(response_data, self.http_client)
                
                await self._event_handler.house_member_exit(ctx, user)

            elif resp['e'] == "PRESENCE_UPDATE":
                precence = types.Presence(response_data, self.http_client)
                user = types.Member(response_data, self.http_client, None) # In work
                await self._event_handler.presence_update(precence, user)

            elif resp['e'] == "MESSAGE_CREATE":
                if self._ready:
                    if response_data.get('house_id') != None:
                        house = utils.get(self._houses, id=int(response_data.get('house_id')))
                    else:
                        house = None
                        
                    room = utils.get(self._rooms, id=int(response_data['room_id']))
                    
                    # Removing the old user and appending the new data so it's up-to-date
                    cached_author = utils.get(self._users, id=int(response_data['author_id']))
                    if response_data.get('author') != None:
                        author = types.User(response_data['author'], self.http_client)
                        
                        if cached_author:
                            self._users.remove(cached_author)
                        self._users.append(author)
                    else:
                        author = cached_author
                    
                    message = types.Message(response_data, self.http_client, house, room, author)
                    await self._event_handler.message_create(message)

            elif resp['e'] == "MESSAGE_DELETE":
                message = types.DeletedMessage(response_data)
                await self._event_handler.message_delete(message)

            elif resp['e'] == "MESSAGE_UPDATE":
                if self._ready:
                    if response_data.get('house_id') != None:
                        house = utils.get(self._houses, id=int(response_data.get('house_id')))
                    else:
                        house = None
                        
                    room = utils.get(self._rooms, id=int(response_data['room_id']))
                    
                    cached_author = utils.get(self._users, id=int(response_data['author_id']))
                    if response_data.get('author') != None:
                        author = types.User(response_data['author'], self.http_client)
                        
                        if cached_author:
                            self._users.remove(cached_author)
                        self._users.append(author)
                    else:
                        author = cached_author
                    
                    message = types.Message(response_data, self.http_client, house=house, room=room, author=author)
                    await self._event_handler.message_update(message)

            elif resp['e'] == "TYPING_START":
                member = types.Typing(response_data, self.http_client)
                await self._event_handler.typing_start(member)

            elif resp['e'] == "TYPING_END":
                member = types.Typing(response_data, self.http_client)
                await self._event_handler.typing_end(member)
            
            # Unknown for now
            elif resp['e'] == "HOUSE_MEMBERS_CHUNK":
                return
            else:
                logger.debug(f"[WEBSOCKET] << Unknown Event {resp['e']} without Handler")
            
        except Exception as e:
            logger.debug(f"[WEBSOCKET] << Failed to catch and handle Event in the websocket! " 
                         f"Cause of Error: {sys.exc_info()[1].__class__.__name__}, {str(e)}")
        
        return
    
