
import discord

from provider import magicshopprovider, staticshopprovider, postsprovider
from commands import homebrewcommands, magicshopcommands, serverinitializationcommands, characterscommands, \
    magicshopreactions, staticshopcommands, staticshopreactions, postscommands, postsreactions


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
            handled: bool = await serverinitializationcommands.handle_server_initialization_prompts(message)
            if not handled:
                handled = await magicshopcommands.handle_shop_commands(message, client)
            if not handled:
                handled = await staticshopcommands.handle_static_shop_commands(message)
            if not handled:
                handled = await characterscommands.handle_character_commands(message, client)
            if not handled:
                handled = await postscommands.handle_posts_commands(message)
            if not handled:
                await homebrewcommands.handle_homebrew_commands(message, client)

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id:
            return
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != client.user.id:
            return
        if channel.id == magicshopprovider.get_shop_channel_id()\
                and payload.message_id == magicshopprovider.get_shop_message_id():
            await magicshopreactions.handle_magic_shop_reaction(payload, channel, client, message)
        elif channel.id == staticshopprovider.get_static_shop_channel_id():
            await staticshopreactions.handle_static_shop_reactions(payload, client, message)
        elif postsprovider.post_section_exists(channel.id):
            await postsreactions.handle_posts_reactions(payload, channel, client, message)

    client.run(bot_token)
