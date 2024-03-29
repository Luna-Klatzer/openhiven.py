""" Test-file for testing purposes and development! """
import logging

import openhivenpy
from openhivenpy import Message

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = openhivenpy.UserClient()


@client.event() 
async def on_ready():
    print(f"Ready after {client.startup_time}")


@client.event()
async def on_message_create(msg: Message):
    print(f"Message was created - {msg.content}")


if __name__ == '__main__':
    client.run("Insert token")
