import logging

import openhivenpy as hiven

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = hiven.UserClient()


@client.event()
async def on_ready():
    print("Bot is ready")

@client.event()
async def on_user_update(self, old, new):
    print(f"{old.name} updated their account")


@client.event()
async def on_message_create(self, msg):
    print(f"{msg.author.name} wrote in {msg.room.name}: {msg.content}")


client.run("Insert token")
