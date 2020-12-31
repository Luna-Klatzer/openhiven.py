#Created by Robyn at 29/11/2020, at precisely 00:58.28 GMT-00. We're in the end game people.
#Yes, this is meant to act as a real life usage example. For testing.

import openhivenpy
import asyncio
import time
import logging

logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = openhivenpy.UserClient(token="")
init = time.time()

@bot.event
async def on_ready(time):
    print(f"Init'd")

@bot.event
async def on_message_create(message):
    if message.content == ".ping": # Until theres a command handler, might as well go old-school discord.py
        await message.room.send(":table_tennis_paddle_and_ball:!")

if __name__ == '__main__':
    bot.run()
