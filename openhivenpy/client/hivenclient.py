import asyncio
import requests

from openhivenpy.Websocket import Websocket

API_URL = "https://api.hiven.io"
API_VERSION = "v1"

class HivenClient(Websocket):
    def __init__(self, client_type: str):
        if client_type == "user":
            self.client_type = UserClient
        elif client_type == "bot":
            self.client_type = BotClient
        else:
            raise ValueError(f"Expected 'user' or 'bot', got '{client_type}'")

        super().__init__(API_URL, API_VERSION)

    def connect(self, TOKEN):
        pass


class UserClient(HivenClient):
    def __init__(self):
        self.client_type = "user"

    def __repr__(self):
        return self.client_type

    def __str__(self):
        return self.client_type


class BotClient(HivenClient):
    def __init__(self):
        self.client_type = "bot"

    def __repr__(self):
        return self.client_type

    def __str__(self):
        return self.client_type


