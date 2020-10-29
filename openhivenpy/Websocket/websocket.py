import requests
import websocket
import asyncio
import json
import time
import sys
import json
import openhivenpy.Types as types
try:
    import thread
except ImportError:
    import _thread as thread

class Websocket():
    def __init__(self, api_url: str, api_version: str, debug_mode: bool, print_output: bool, token: str, heartbeat: int or float):
        self.api_url = api_url
        self.api_version = api_version

        self.WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
        self.ENCODING = "json"
        self.TOKEN = token

        self.PRINT_OUTPUT = print_output
        self.debug_mode = debug_mode
        self.HEARTBEAT = heartbeat

        # Activate Debug Mode for a lot of spam
        websocket.enableTrace(True) if debug_mode == True else None

        self.connection_status = "closed"
        # Creating the WebSocket that will listen to the API and general events
        self.hiven_websocket = websocket.WebSocketApp(self.WEBSOCKET_URL, on_message=lambda websocket, msg: self.on_resp_message(websocket, msg), 
                                                on_open=lambda ws: self.on_open(ws), on_error=self.on_error, on_close=self.on_close)

    # Opens the event loop. Thanks for the nice work NexInfinite/hivenpy
    def on_open(self, hiven_websocket):
        try:
            hiven_websocket.send('{"op": 2, "d":{"token": "' + self.TOKEN + '"}}')

            def start_connection():
                while True:
                    time.sleep(self.HEARTBEAT / 1000)
                    hiven_websocket.send('{"op": 3}')
                    if self.connection_status == "closing" or self.connection_status == "closed":
                        break
                return 

            self.connection_status = "open"
            thread.start_new_thread(start_connection, ())

        except Exception as e:
            raise Exception(f"An error appeared while trying to connect to Hiven.\n{e}")

    def on_resp_message(self, hiven_websocket, ctx):
        data = json.loads(ctx)
        print(data["e"])
        if data["e"] == "HOUSE_JOIN":
            print(types.House(data["d"]).name)


    def on_error(self, hiven_websocket, error):
        raise Exception(error)

    def on_close(self, hiven_websocket):
        try:
            asyncio.get_event_loop().stop()
            asyncio.get_event_loop().close()
            self.connection_status = "closed"

        except Exception as e:
            raise Exception(f"An error appeared while closing the connection to Hiven.\n{e}")

    async def get(self, keyword: str = "", headers={'content_type': 'text/plain'}):
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp


    # Does not work yet
    async def start_and_close_event_loop(self, websocket=None):

        ws = self.hiven_websocket if websocket == None else websocket

        ws.send('{"op": 2, "d":{"token": "' + self.TOKEN + '"}}')
        
        def start_connection():
            i = 0
            while i < 1000:
                time.sleep(self.HEARTBEAT / 1000)
                ws.send('{"op": 3}')
                if self.connection_status != "closing" or self.connection_status != "closed":
                    break
                i += 1
            return 

        thread.start_new_thread(start_connection, ())

        # Waiting 5 seconds before actually closing the websocket
        await asyncio.sleep(5)
        ws.close()


    async def start_event_loop(self, websocket=None):
        # If the user specifies a websocket that one will be used here else the default Hiven Websocket will be used
        ws = self.hiven_websocket if websocket == None else websocket

        ws.run_forever()

    async def stop_event_loop(self, websocket=None):
        try:
            # If the user specifies a websocket that one will be used here else the default Hiven Websocket will be used
            ws = self.hiven_websocket if websocket == None else websocket

            self.connection_status = "closing"
            ws.close()
            asyncio.get_event_loop().stop()
            asyncio.get_event_loop().close()

        except Exception as e:
            raise Exception(f"An error appeared while trying to close the connection to Hiven.{e}")

    async def get_connection_status(self):
        return self.connection_status
