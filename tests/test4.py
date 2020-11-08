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
TOKEN = os.getenv("token") or "" #Just to prevent mishaps
event_loop = asyncio.new_event_loop()
client = openhivenpy.UserClient(token=TOKEN, event_loop=event_loop)

@client.event() 
async def on_init(time):
    print("Init'd")

async def run():
    response = await client.get()

    # If response is 200 that means the program can interact with Hiven
    if response.status_code == 200:
        print("Success!")
    else:
        print(f"The process failed. STATUSCODE={response.status_code}")

    # Starts the Event loop with the a specified websocket 
    # => can also be a different websocket
    await client.create_connection()
    asyncio.set_event_loop(asyncio.new_event_loop())


if __name__ == '__main__':
    asyncio.run(run())