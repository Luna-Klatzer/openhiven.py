import asyncio
import requests
import sys
import warnings

from openhivenpy.Websocket import Websocket
import openhivenpy.Error.Exception as errs #Kinda started working on this before I pulled lol

API_URL = "https://api.hiven.io"
API_VERSION = "v1"

class HivenClient(Websocket):
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
            raise errs.InvalidToken("Invalid Token was passed!")

        self.heartbeat = heartbeat
        self.token = token
        self.debug_mode = bool(debug_mode)
        self.print_output = bool(print_output)

        super().__init__(API_URL, API_VERSION, self.debug_mode, self.print_output, self.token, self.heartbeat)

    async def deactivate_print_output(self):
        try:
            self.PRINT_OUTPUT = False
        except AttributeError as e:
            raise errs.NoDisplayInfo(f"The attribute display_info_mode does not exist! The HivenClient Object was possibly not initialized correctly!\n{e}")
        except Exception as e:
            sys.stdout.write(str(e))

    async def connect(self, TOKEN):
        self.start_event_loop(TOKEN)

    # Just for ease
    def run(self):
        asyncio.run(self.start_event_loop())

class UserClient(HivenClient):
    def __init__(self, token: str, heartbeat=0, debug_mode=False, print_output=False):
        self.client_type = "HivenClient.UserClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, print_output=print_output, debug_mode=debug_mode)

    def __repr__(self):
        return str(self.client_type)

    def __str__(self):
        return str(self.client_type)


# Basically not useable at the moment because it does not exist
class BotClient(HivenClient):
    def __init__(self, token: str, heartbeat=0, debug_mode=False, print_output=False):
        self.client_type = "HivenClient.BotClient"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, print_output=print_output, debug_mode=debug_mode)

    def __repr__(self):
        return str(self.client_type)

    def __str__(self):
        return str(self.client_type)



