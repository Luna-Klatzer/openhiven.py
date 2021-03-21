import openhivenpy
import logging


logger = logging.getLogger("openhivenpy")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='openhiven.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = openhivenpy.UserClient()


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_message_create(message):
    # Until theres a command handler, might as well go old-school discord.py
    if message.content == ".ping":
        await message.room.send(":table_tennis_paddle_and_ball:!")

if __name__ == '__main__':
    bot.run("Insert token",)
