#Created by Robyn at 29/11/2020, at precisely 00:58.28 GMT-00. We're in the end game people.
#Yes, this is meant to act as a real life usage example. For testing.

import openhivenpy
import asyncio
import time
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = openhivenpy.UserClient(token="")
init = time.time()

@bot.event
async def on_ready():
    print(f"Init'd in {time.time() - 1}")

@bot.event
async def on_message_create(message):
    if message.content == "ping":
        await message.room.send(content=":table_tennis_paddle_and_ball:!",delay=0)

async def run():
    # If response is 200 that means the program can interact with Hiven
    if bot.connection_possible:
        print("Success!")
    else:
        print(f"The ping failed!")

    # Starts the Event loop with the specified websocket  
    # => can also be a different websocket
    bot.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())