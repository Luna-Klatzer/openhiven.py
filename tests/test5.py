import openhivenpy
import asyncio
import os
import logging

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Simple test to get a simple response from the Hiven API
TOKEN = os.getenv("token") or "" #Dear MS, MAKE VSC TERMINAL SUPPORT FILE ENVS!
event_loop = asyncio.new_event_loop()
client = openhivenpy.UserClient(token=TOKEN, event_loop=event_loop)

@client.event()
async def on_connection_start():
    print("Connection established")

@client.event()
async def on_init(time):
    print("Init'd")

@client.event() 
async def on_ready(ctx):
    print("Ready")
    
    house = await client.get_house(175036727902074248)
    room = await house.get_room(175036775851357578)
    await room.edit(emoji="page_with_curl")
    print(client.startup_time)

@client.event()
async def on_message_create(message):
    print(message.room.id)

async def run():
    # If response is 200 that means the program can interact with Hiven
    if client.connection_possible:
        print("Success!")
    else:
        print(f"The ping failed!")

    # Starts the Event loop with the specified websocket  
    # => can also be a different websocket
    await client.connect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())