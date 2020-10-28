import requests
import websocket
import asyncio
import json
import time
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

        # Creating the WebSocket that will listen to the API and general events
        self.websocket = websocket.WebSocketApp(self.WEBSOCKET_URL, on_message=lambda websocket, msg: self.on_resp_message(websocket, msg), 
                                                on_open=lambda resp_websocket: self.on_open(resp_websocket), on_error=self.on_error, on_close=self.on_close)

    # Opens the event loop. Thanks for the nice work NexInfinite/hivenpy
    def on_open(self, websocket):
        websocket.send('{"op": 2, "d":{"token": "' + self.TOKEN + '"}}')

        def run():
            while True:
                time.sleep(self.HEARTBEAT / 1000)
                websocket.send('{"op": 3}')

        thread.start_new_thread(run, ())

    def on_resp_message(self, websocket, ctx):
        # print(json.loads(ctx))
        pass

    def on_error(self, websocket, error):
        raise Exception(error)

    def on_close(self, websocket):
        asyncio.get_event_loop().stop()
        asyncio.get_event_loop().close()

    async def get(self, keyword: str = "", headers={'content_type': 'text/plain'}):
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp

    async def start_and_close_event_loop(self, websocket):
        try:
            websocket.run_forever()
            await asyncio.sleep(5)
            websocket.close()
        except Exception as e:
            print(e)
            return 

    async def start_event_loop(self, websocket):
        try:
            websocket.run_forever()
        except Exception as e:
            print(e)
            return 

    async def end_event_loop(self):
        try:
            websocket.close()
            asyncio.get_event_loop().stop()
            asyncio.get_event_loop().close()
        except Exception as e:
            print(e)
            return 

