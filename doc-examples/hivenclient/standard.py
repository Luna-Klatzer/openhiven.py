import logging

import openhivenpy as hiven

logging.basicConfig(level=logging.INFO)

client = hiven.UserClient()


@client.event()
async def on_ready():
    print("Bot is ready")


client.run("Insert token")
