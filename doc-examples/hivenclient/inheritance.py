import openhivenpy as hiven
import logging

from openhivenpy.utils import utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


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

    async def on_message_create(self, msg):
        print(f"{msg.author.name} wrote in {msg.room.name}: {msg.content}")

    async def on_house_member_join(self, member, house):
        print(f"{member.name} joined {house.name}")


if __name__ == '__main__':
    client = Bot(token="")
    client.run()
