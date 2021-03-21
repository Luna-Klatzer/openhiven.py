import openhivenpy as hiven
import logging

logging.basicConfig(level=logging.INFO)

client = hiven.UserClient()


@client.event()
async def on_ready():
    print("Bot is ready")

client.run("Insert token")
