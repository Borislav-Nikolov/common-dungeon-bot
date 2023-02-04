import discord
import os

import firebase
import magicshop
from dotenv import load_dotenv

load_dotenv()


def run_discord_bot():
    bot_token = str(os.getenv('TEST_TOKEN'))
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            if str(message.content).startswith('1)') or str(message.content).startswith('~~'):
                firebase.set_shop_message_id(message.id)
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if message.channel.name == '💰-shop' and user_message == '$generate':
            await message.channel.send(magicshop.generate_new_magic_shop())
        if message.channel.name == '💰-shop' and len(user_message) >= 3 and user_message[0] == '$' and user_message[1:3].isnumeric():
            shop_message = await message.channel.fetch_message(firebase.shop_message_ref.get()["message_id"])
            shop_string = magicshop.sell_item(int(user_message[1:3]))
            await shop_message.edit(content=shop_string)
            await message.add_reaction('🪙')
        elif user_message.lower().startswith('bogdy'):
            if 'give me love' in user_message.lower():
                await message.add_reaction('❤')
            else:
                await message.channel.send('Sorry, I\'m quite busy at the moment.')

    client.run(bot_token)
