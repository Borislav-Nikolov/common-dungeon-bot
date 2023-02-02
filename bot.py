import discord
import responses
import os
from dotenv import load_dotenv

load_dotenv()

channels_to_messages = dict()

# react with 🪙
# add reactions to chronicles channel posts - 'heart'
# use firebase to store data?


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    bot_token = str(os.getenv('token'))
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

        if user_message[0] == '@':
            await message.add_reaction('🪙')
        elif user_message[0] == '!':
            user_message = user_message[1:]
            last_bot_message = await message.channel.fetch_message(channels_to_messages[message.channel.id])
            await last_bot_message.edit(content=user_message)
        elif user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    client.run(bot_token)
