import discord
import os
import magicshop
from dotenv import load_dotenv

load_dotenv()

channels_to_messages = dict()

# react with 🪙
# add reactions to chronicles channel posts - 'heart'
# use firebase to store data?


def run_discord_bot():
    bot_token = str(os.getenv('TOKEN'))
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            global channels_to_messages
            try:
                channels_to_messages[message.channel.id] = message.id
            except Exception as e:
                print(e)
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if message.channel.name == '💰-shop' and user_message == '$generate':
            await message.channel.send(magicshop.get_item_names())

    client.run(bot_token)
