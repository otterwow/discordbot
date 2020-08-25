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


client.run("NzQ1OTk4ODcyNjA1NzUzMzc3.Xz57lw.kGh0I8-iYPB0xtFpQ87jgHj2ntk")
