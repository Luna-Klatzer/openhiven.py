import openhivenpy
import asyncio
import os
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='tests/openhiven.log', encoding='utf-8', mode='w')
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

    print(friend_request)

    # await client.create_private_room()


@client.event()
async def on_message_create(message):
    print(message.content)


@client.event()
async def on_house_add(house):
    print(house.name)


@client.event()
async def on_house_remove(house):
    print(house.name)


@client.event()
async def on_house_downage(t, house):
    print(f"{house.name} was reported to be done at {t}")


@client.event()
async def on_typing_start(typing):
    print(typing)


@client.event()
async def on_house_exit(user, house):
    print(f"{user.name} left {house.name}")


@client.event()
async def on_house_enter(member, house):
    print(f"{member.name} joined {house.name}")

if __name__ == '__main__':
    client.run()
