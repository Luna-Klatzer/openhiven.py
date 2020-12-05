import openhivenpy
import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Simple test to get a simple response from the Hiven API
TOKEN = os.getenv("token") or ""
event_loop = asyncio.new_event_loop()
client = openhivenpy.UserClient(
                                token=TOKEN,
                                event_loop=event_loop)


@client.event()
async def on_connection_start():
    print("Connection established")


@client.event()
async def on_init(time):
    print(f"Init'd at {time}")


@client.event() 
async def on_ready():
    print(f"Ready after {client.startup_time}")

    house = await client.get_house(175036727902074248)

    url = await client.fetch_invite("openhivenpy")
    
    house = await client.create_house("test house")

    house = openhivenpy.utils.get(client.houses, id=house.id)

    await house.create_room(name="stuff")
    
    room = house.rooms[0]
    
    await room.send("test")
    
    await house.delete()
    
    feed = await client.get_feed()
    
    mentions = await client.get_mentions()
    
    friend_request = await client.fetch_current_friend_requests()
    
    private_room = await client.get_private_room(175699760957616349)
    
    # await client.create_private_room() # Robyn please find some random users and open private rooms with them #no # sad noises


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
    client.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())