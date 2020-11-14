import openhivenpy
import asyncio
import logging

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Simple test to get a simple response from the Hiven API
client = openhivenpy.UserClient:

if client.connection_possible():
    print("Success")
else:
    print(f"The attempt to ping Hiven failed!")
