"""
Test-file for testing purposes and development!
"""
import asyncio
import time
import openhivenpy
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = openhivenpy.UserClient(
    ""
)


@client.event() 
async def on_ready():
    print(f"Ready after {client.startup_time}")

if __name__ == '__main__':
    client.run()
