import openhivenpy
import asyncio
import sys
import os
import logging

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Simple test to get a simple response from the Hiven API
TOKEN = os.getenv("token") or "TOKEN" #Just to prevent mishaps
client = openhivenpy.UserClient(token=TOKEN, heartbeat=10)

if client.connection_possible:
    print("Success")
else:
    print(f"The attempt to ping Hiven failed!")

# Starts the Event loop with the a specified websocket => can also be a different websocket
client.run()
