import asyncio
import requests
import sys
import warnings

from openhivenpy.Websocket import Websocket
from openhivenpy.Events import Events
import openhivenpy.Error.Exception as errs

API_URL = "https://api.hiven.io"
API_VERSION = "v1"

class HivenClient(Websocket, Events):
    def __init__(self, token: str, client_type: str = "user",  heartbeat=0, print_output=False, debug_mode=False):
        if client_type == "user" or client_type == "HivenClient.UserClient":
            self.client_type = "HivenClient.UserClient"
        elif client_type == "bot" or client_type == "HivenClient.BotClient":
            self.client_type = "HivenClient.BotClient"
        elif client_type == None:
            warnings.warn(errs.NoneClientType("Client type is None. Defaulting to BotClient."))
            self.client_type = "HivenClient.BotClient"
        else:
            raise errs.InvalidClientType(f"Expected 'user' or 'bot', got '{client_type}'") #Could use the diff lib here, and if that doesnt get anything then raise an error :thinking:
        
        if token == None or token == "":
            raise errs.InvalidToken("Token was not set")
        elif len(token) != 128:
            raise errs.InvalidToken("Invalid Token")

        super().__init__(API_URL, API_VERSION, debug_mode, print_output, token, heartbeat)

    async def deactivate_print_output(self):
        try:
            self.PRINT_OUTPUT = False
        except AttributeError as e:
            raise errs.NoDisplayInfo(f"The attribute display_info_mode does not exist! The HivenClient Object was possibly not initialized correctly!\n{e}")
        except Exception as e:
            sys.stdout.write(str(e))

    async def connect(self, token=None):
        connection = await self.create_connection()
        return connection

    # Just for ease
    def run(self):
        asyncio.run(self.start_event_loop())
        



