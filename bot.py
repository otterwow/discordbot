import os
import discord
from process_input import process as process_input

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await process_input(message)


token = os.environ['BOT_TOKEN']
client.run(token)
