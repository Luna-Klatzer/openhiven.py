import openhivenpy as hiven
import logging

logging.basicConfig(level=logging.INFO)


class Bot(hiven.UserClient):
    def __init__(self, token):
        self._token = token
        super().__init__(token)

    # Not directly needed but protects the token from ever being changed!
    @property
    def token(self):
        return self._token

    async def on_ready(self):
        print("Bot is ready!")


if __name__ == '__main__':
    client = Bot(token="Insert token here")
    client.run()
