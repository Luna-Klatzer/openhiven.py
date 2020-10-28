import asyncio
import requests

from openhivenpy.Websocket import Websocket
import openhivenpy.Error as err

API_URL = "https://api.hiven.io"
API_VERSION = "v1"

class HivenClient(Websocket):
    def __init__(self, token: str, client_type: str = "user",  heartbeat=0, print_output=False, debug_mode=False):
        if client_type == "user":
            self.client_type = UserClient
        elif client_type == "bot":
            self.client_type = BotClient
        else:
            raise ValueError(f"Expected 'user' or 'bot', got '{client_type}'")

        self.heartbeat = heartbeat
        self.token = token
        self.debug_mode = debug_mode
        self.print_output = print_output

        super().__init__(API_URL, API_VERSION, self.debug_mode, self.print_output, self.token, self.heartbeat)

    async def deactivate_print_output(self):
        try:
            self.PRINT_OUTPUT = False
        except AttributeError:
            raise AttributeError("The attribute display_info_mode does not exist! The HivenClient Object was possibly not initialized correctly!")
        except Exception as e:
            print(e)

    async def connect(self, TOKEN):
        self.start_event_loop(TOKEN)

class UserClient(HivenClient):
    def __init__(self, token: str, heartbeat=0, debug_mode=False, print_output=False):
        self.client_type = "user"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, print_output=False, debug_mode=False)

    def __repr__(self):
        return self.client_type

    def __str__(self):
        return self.client_type


# Basically not useable at the moment because it does not exist
class BotClient(HivenClient):
    def __init__(self, token: str, heartbeat=0, debug_mode=False, print_output=False):
        self.client_type = "bot"
        super().__init__(token=token, client_type=self.client_type, heartbeat=heartbeat, print_output=False, debug_mode=False)

    def __repr__(self):
        return self.client_type

    def __str__(self):
        return self.client_type



