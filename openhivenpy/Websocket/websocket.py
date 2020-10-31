import requests
import websockets
import asyncio
import json
import time
import sys
import json

import openhivenpy.Types as types
import openhivenpy.Error.Exception as errs

class Websocket():
    def __init__(self, api_url: str, api_version: str, debug_mode: bool, print_output: bool, token: str, heartbeat: int or float):
        self.api_url = api_url
        self.api_version = api_version

        self.WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self.ENCODING = "json"
        self.TOKEN = token

        self.HEARTBEAT = heartbeat
        self.debug_mode = debug_mode
        self.print_output = print_output

        self.connection_status = "closed"


    # Starts the connection over a new websocket
    async def create_connection(self, heartbeat: int or float = None):

        self.HEARTBEAT = heartbeat if heartbeat != None else self.HEARTBEAT

        async def websocket_connect():
            try:
                async with websockets.connect(uri=self.WEBSOCKET_URL) as websocket:
                    # Sending the token and authorizing with it
                    await websocket.send(json.dumps({"op": 2, "d": {"token": str(self.TOKEN)}}))

                    # Receiving the first response from Hiven and setting the specified heartbeat
                    response = json.loads(await websocket.recv())
                    if response['op'] == 1 and self.HEARTBEAT != 30000:
                        self.HEARTBEAT = response['d']['hbt_int']

                    # Messages will be sent and received paralell, so that both don't block each other
                    await asyncio.gather(self.on_open(websocket), self.receive_message(websocket))

            except Exception as e:
                await self.on_error(websocket, e)

        connection = asyncio.create_task(websocket_connect())
        # Running the task in the background
        await connection

        self.connection = connection

        return connection

    # Loop for receiving messages from Hiven
    async def receive_message(self, ws):
        while True:
            response = await ws.recv()
            if response != None:
                await self.on_response(ws, response)

    # Opens the event loop
    async def on_open(self, ws):
        try:
            async def start_connection():
                while True:
                    await asyncio.sleep(self.HEARTBEAT / 1000)
                    await ws.send(json.dumps({"op": 3}))
                    if self.connection_status == "closing" or self.connection_status == "closed":
                        break
                return 

            self.connection_status = "open"

            connection = asyncio.create_task(start_connection())
            await connection

        except Exception as e:
            raise errs.UnableToConnect(f"An error occured while trying to connect to Hiven.\n{e}")

    async def on_error(self, ws, error):
        raise Exception(error)

    async def on_response(self, ws, ctx_data):
        response_data = json.loads(ctx_data)

        if response_data['e'] == "INIT_STATE":
            client = types.Client(response_data['d'])
            await self.INIT_STATE(client)

        elif response_data['e'] == "HOUSE_JOIN":
            ctx = types.Context(response_data['d'])
            client = types.Client(response_data['d'])
            await self.HOUSE_JOIN(ctx, client)

        elif response_data['e'] == "HOUSE_MEMBER_ENTER":
            ctx = types.Context(response_data['d'])
            member = types.Member(response_data['d'])
            await self.HOUSE_MEMBER_ENTER8(ctx, member)

        elif response_data['e'] == "HOUSE_MEMBER_EXIT":
            ctx = types.context(response_data['d'])
            member = types.Member(response_data['d'])
            await self.HOUSE_MEMBER_EXIT(ctx, member)

        elif response_data['e'] == "PRESENCE_UPDATE":
            precence = types.precence(response_data['d'])
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
            member = types.Member(response_data['d'])
            await self.TYPING_START(member)

        elif response_data['e'] == "TYPING_END":
            member = types.Member(response_data['d'])
            await self.TYPING_END(member)

        else:
            print(response_data['e'])

    # Gets a json file from the hiven api
    async def get(self, keyword: str = "", headers={'content_type': 'text/plain'}):
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp

    # Gets the current connection_status
    async def get_connection_status(self):
        return self.connection_status

    # Stops the connection
    async def stop_event_loop(self):
        try:
            # If the user specifies a websocket that one will be used here else the default Hiven Websocket will be used
            ws = self.hiven_websocket if ws == None else ws

            self.connection_status = "closing"
            ws.close()
            asyncio.get_event_loop().stop()
            asyncio.get_event_loop().close()

        except Exception as e:
            raise Exception(f"An error appeared while trying to close the connection to Hiven.{e}")
