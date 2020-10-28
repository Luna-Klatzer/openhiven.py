import requests
import websocket


WEBSOCKET_URL = "wss://swarm-dev.hiven.io/socket?encoding=json&compression=text_json"
ENCODING = "json"

class Websocket():
    def __init__(self, api_url, api_version):
        self.api_url = api_url
        self.api_version = api_version

    async def get(self, keyword: str = "", headers={'content_type': 'text/plain'}):
        resp = requests.get(url=f"{self.api_url}/{keyword}")
        return resp
        