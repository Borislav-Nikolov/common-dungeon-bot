
import discord

from provider import postsprovider
from commands import homebrewcommands, magicshopcommands, serverinitializationcommands, characterscommands, \
    magicshopreactions, staticshopcommands, staticshopreactions, postscommands, postsreactions, charactersreactions, \
    consolecommands, timecommands
from bridge import consolebridge, charactersbridge, magicshopbridge
from util import botutils
from discord.ext import commands
from api import channelsrequests, testapicommunication
import asyncio


global client


def run_discord_bot(bot_token, allowed_guild_id: str):
    intents = discord.Intents.default()
    intents.message_content = True
    global client
    client = commands.Bot(command_prefix='$', intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await consolebridge.reinitialize_console_messages(client)
        await charactersbridge.reinitialize_character_messages(client)
        await asyncio.create_task(
            magicshopbridge.run_automatic_shop_posting(client.get_channel(channelsrequests.get_shop_channel_id())))

    @client.event
    async def on_resumed():
        print(f'{client.user} has been resumed.')
        await consolebridge.reinitialize_console_messages(client)
        await charactersbridge.reinitialize_character_messages(client)

    @client.event
    async def on_disconnect():
        print(f'{client.user} has been disconnected.')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.guild:
            if str(message.guild.id) != allowed_guild_id:
                return

        username = str(message.author.id)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if user_message == '!testapicommunication' and botutils.is_admin_message(message):
            if testapicommunication.test_api_communication():
                await message.add_reaction('🪙')
            else:
                await message.add_reaction('❌')
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
                handled = await homebrewcommands.handle_homebrew_commands(message, client)
            if not handled:
                handled = await consolecommands.handle_console_commands(message, client)
            if not handled:
                await timecommands.handle_time_commands(message)

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id:
            return
        if payload.guild_id:
            if str(payload.guild_id) != allowed_guild_id:
                return
        # use `user` in case payload.member is None - happens in DM channels
        user = await client.fetch_user(payload.user_id)
        try:
            channel = client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
        except AttributeError:
            # attempt to fetch the message from a DM channel with the user
            channel = await user.create_dm()
            message = await channel.fetch_message(payload.message_id)
        if message.author.id != client.user.id:
            return
        if channel.id == channelsrequests.get_shop_channel_id()\
                and payload.message_id == channelsrequests.get_shop_message_id():
            await magicshopreactions.handle_magic_shop_reaction(payload, channel, client, message)
        elif channel.id == channelsrequests.get_static_shop_channel_id():
            await staticshopreactions.handle_static_shop_reactions(payload, client, message)
        elif botutils.is_dm_channel(channel):
            dm_reaction_handled =\
                await charactersreactions.handle_inventory_reaction(payload, user, channel, client, message)
            if not dm_reaction_handled:
                dm_reaction_handled =\
                    await charactersreactions.handle_reserved_item_reaction(payload, user, channel, client, message)
        elif postsprovider.post_section_exists(channel.id):
            await postsreactions.handle_posts_reactions(payload, channel, client, message)

    client.run(bot_token)
