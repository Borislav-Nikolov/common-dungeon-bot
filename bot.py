
import discord

from provider import magicshopprovider
from commands import homebrewcommands, magicshopcommands, serverinitializationcommands, characterscommands, \
    magicshopreactions


def run_discord_bot(bot_token):
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author.id)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if user_message.startswith('$'):
            await serverinitializationcommands.handle_server_initialization_prompts(message)
            await magicshopcommands.handle_shop_commands(message, client)
            await characterscommands.handle_character_commands(message, client)
            await homebrewcommands.handle_homebrew_commands(message, client)

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id:
            return
        channel = client.get_channel(payload.channel_id)
        if channel.id == magicshopprovider.get_shop_channel_id()\
                and payload.message_id == magicshopprovider.get_shop_message_id():
            await magicshopreactions.handle_magic_shop_reaction(payload, channel, client)

    client.run(bot_token)
