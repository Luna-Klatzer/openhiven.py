import requests
import websockets
import asyncio
import json
import time
import sys
import json
import datetime

import openhivenpy.Types as types
import openhivenpy.Error.Exception as errs
import openhivenpy.Utils as utils

class Websocket():
    """openhivenpy.Websocket.Websocket: Websocket 
    
    Websocket Class that will listen to the Hiven Websocket and will listen for Events 
    
    """    
    def __init__(self, api_url: str, api_version: str, debug_mode: bool, print_output: bool, token: str, heartbeat: int or float):
        self._api_url = api_url
        self._api_version = api_version

        self._WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self._ENCODING = "json"
        self._TOKEN = token

        # Heartbeat is the interval where messages are going to get sent. 
        # In miliseconds
        self._HEARTBEAT = heartbeat
        self._debug_mode = debug_mode
        self._print_output = print_output

        self._connection_status = "closed"

        self._open = False
        self._closed = True

        self._connection_start = None
        self._startup_time = None

        if not hasattr(self, '_CUSTOM_HEARBEAT'):
            raise errs.FaultyInitializationError("The client attribute _CUSTOM_HEARTBEAT does not exist! The class might be initialized faulty!")

    @property
    def api_url(self) -> str:
        return self._api_url

    @property
    def api_version(self) -> str:
        return self._api_version

    @property
    def websocket_url(self) -> str:
        return self._WEBSOCKET_URL

    @property
    def encoding(self) -> str:
        return self._ENCODING

    @property
    def token(self) -> str:
        return self._TOKEN

    @property
    def heartbeat(self) -> int:
        return self._HEARTBEAT

    @property
    def debug_mode(self) -> bool:
        return self._debug_mode

    @property
    def print_output(self) -> bool:
        return self._print_output

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
    def websocket(self) -> websockets.client.WebSocketClientProtocol:
        """
        
        Returns the ReadOnly Websocket with it's configuration
        
        """    
        return self._websocket

    @property
    def initalized(self) -> bool:
        return self._initalized

    @property
    def connection_start(self) -> float:
        return self._connection_start

    @property
    def startup_time(self) -> float:
        return self._startup_time

    # Starts the connection over a new websocket
    async def create_connection(self, heartbeat: int or float = None) -> None:
        """
        
        Creates a connection to the Hiven API. Not supposed to be called by the user! Rather use HivenClient.connect() or HivenClient.run()
        
        """        

        self._HEARTBEAT = heartbeat if heartbeat != None else self._HEARTBEAT

        async def websocket_connect() -> None:
            try:
                # Connection Start variable for later calculation the time how long it took to start
                self._connection_start = time.time()

                async with websockets.connect(uri=self._WEBSOCKET_URL, ping_timeout=100, close_timeout=20, ping_interval=60) as websocket:

                    websocket = await self.websocket_init(websocket)

                    # Sending the token and authorizing with it
                    await websocket.send(json.dumps({"op": 2, "d": {"token": str(self._TOKEN)}}))

                    # Receiving the first response from Hiven and setting the specified heartbeat
                    response = json.loads(await websocket.recv())
                    if response['op'] == 1 and self._CUSTOM_HEARBEAT == False:
                        self._HEARTBEAT = response['d']['hbt_int']
                        websocket.heartbeat = self._HEARTBEAT

                    self._closed = websocket.closed
                    self._open = websocket.open

                    # Triggering the user event for the connection start
                    await self.ON_CONNECTION_START()

                    # Messages will be sent and received paralell
                    # => both won't block each other
                    await asyncio.gather(self.on_open(websocket), self.receive_message(websocket))

            except Exception as e:
                # Getting the place of error(line of error) 
                # and appending it to the error message
                try: line_of_error = sys.exc_info()[-1].tb_lineno
                except Exception as e: line_of_error = "Unknown"

                await self.on_error(f"In Line {line_of_error}: " + str(e).capitalize())

        connection = asyncio.create_task(websocket_connect())
        # Running the task in the background
        await connection

        self._connection = connection

        return

    # Passing values to the Websocket for more information while executing
    async def websocket_init(self, websocket) -> websockets.client.WebSocketClientProtocol:
        """
        
        Initialization Function for the Websocket. Not supposed to be called by user!
        
        """        
        websocket.url = self._WEBSOCKET_URL
        websocket.heartbeat = self._HEARTBEAT
        websocket.debug_mode = self._debug_mode

        self._websocket = websocket

        return self.websocket

    # Loop for receiving messages from Hiven
    async def receive_message(self, websocket) -> None:
        """
        
        Handler for Receiving Messages. Not supposed to be called by the user! 
        
        """      
        while True:
            response = await websocket.recv()
            if response != None:
                await self.on_response(websocket, response)

    # Opens the event loop
    async def on_open(self, websocket) -> None:
        """
        
        Handler for Opening the Websocket. Not supposed to be called by the user! 
        
        """    
        try:
            async def start_connection():
                while True:
                    # Sleeping the wanted time (Pause for the Heartbeat)
                    await asyncio.sleep(self._HEARTBEAT / 1000)

                    if self._debug_mode == True: print(f"[OPENHIVEN_PY] >> WEBSOCKET ON '{self._WEBSOCKET_URL}' [{datetime.datetime.now().strftime('%H:%M:%S:%f')}] Data was sent!") 

                    # Sending messages to the Hiven Api to show a live Signal
                    await websocket.send(json.dumps({"op": 3}))

                    # If the connection is closing the loop will break
                    if self._connection_status == "closing" or self._connection_status == "closed":
                        break

                return 

            self._connection_status = "open"

            connection = asyncio.create_task(start_connection())
            await connection

        except Exception as e:
            raise errs.UnableToConnect(f"An error occured while trying to connect to Hiven.\n{e}")

    # Error Handler for exceptions while running the websocket connection
    async def on_error(self, error) -> None:
        """
        
        Handler for Errors in the Websocket. Not supposed to be called by the user! 
        
        """    
        raise sys.exc_info()[0](error)

    async def on_response(self, websocket, ctx_data) -> None:
        """
        
        Handler for the Websocket Events and the message data. Not supposed to be called by the user! 
        
        """    
        response_data = json.loads(ctx_data)

        print(response_data) if self._print_output == True else None

        if response_data['e'] == "INIT_STATE":
            client = self.update_client_data(response_data['d'])
            await self.INIT_STATE(client)
            self._initalized = True

        elif response_data['e'] == "HOUSE_JOIN":
            if not hasattr(self, '_HOUSES') and not hasattr(self, '_USERS'):
                raise errs.FaultyInitializationError("The client attributes _USERS and _HOUSES do not exist! The class might be initialized faulty!")

            ctx = types.House(response_data['d'])
            await self.HOUSE_JOIN(ctx)
            self._HOUSES.append(ctx)

            for usr in response_data["d"]["users"]:
                if not utils.get(self._USERS,id=usr["id"]):
                    self._USERS.append(types.User(usr))         

        elif response_data["e"] == "HOUSE_EXIT":
            ctx = types.Context(response_data['d'])
            await self.HOUSE_EXIT(ctx)

        elif response_data["e"] == "HOUSE_DOWN":
            house = None #ToDo
            await self.HOUSE_DOWN(house)
            

        elif response_data['e'] == "HOUSE_MEMBER_ENTER":
            ctx = types.Context(response_data['d'])
            member = types.Member(response_data['d'])
            await self.HOUSE_MEMBER_ENTER8(ctx, member)

        elif response_data['e'] == "HOUSE_MEMBER_EXIT":
            ctx = types.Context(response_data['d'])
            member = types.Member(response_data['d'])
            await self.HOUSE_MEMBER_EXIT(ctx, member)

        elif response_data['e'] == "PRESENCE_UPDATE":
            precence = types.Precence(response_data['d'])
            member = types.Member(response_data['d'])
            await self.PRESENCE_UPDATE(precence, member)

        elif response_data['e'] == "MESSAGE_CREATE":
            message = types.Message(response_data['d'])
            await self.MESSAGE_CREATE(message)

        elif response_data['e'] == "MESSAGE_DELETE":
            message = types.Message(response_data['d'])
            await self.MESSAGE_DELETE(message)

        elif response_data['e'] == "MESSAGE_UPDATE":
            message = types.Message(response_data['d'])
            await self.MESSAGE_UPDATE(message)

        elif response_data['e'] == "TYPING_START":
            member = types.Typing(response_data['d'])
            await self.TYPING_START(member)

        elif response_data['e'] == "TYPING_END":
            member = types.Typing(response_data['d'])
            await self.TYPING_END(member)
        

        else:
            print(response_data['e'])
            
        return

    # Gets a json file from the hiven api
    async def get(self, keyword: str = "", headers={'content_type': 'application/json'}) -> dict:
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp

    # Gets the current connection_status
    async def get_connection_status(self) -> str:
        return self.connection_status

    # Stops the websocket connection
    async def stop_event_loop(self) -> None:
        try:
            self._connection_status = "closing"
            asyncio.get_event_loop().stop()
            asyncio.get_event_loop().close()

        except Exception as e:
            raise Exception(f"An error appeared while trying to close the connection to Hiven.{e}")
        
        return
