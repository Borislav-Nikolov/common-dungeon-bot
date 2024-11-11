from util import utils, botutils
from discord import TextChannel, Message
from discord.ui import View
from bridge import consolebridge


async def handle_console_commands(message, client) -> bool:
    console_key = '$console'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == console_key:
        # ADMIN COMMANDS
        if botutils.is_admin_message(message):
            if keywords[1] == 'inventory':
                await handle_console_inventory_prompt(message.channel)
                return True
            if keywords[1] == 'shopgenerate':
                await handle_console_shop_generate_prompt(message.channel, client)
                return True
            if keywords[1] == 'characterstatus':
                await handle_console_change_status_prompt(message.channel, client)
            if keywords[1] == 'reserveditems':
                await handle_console_reserved_items_prompt(message.channel)
            if keywords[1] == 'reinitialize':
                await handle_console_reinitialize(message, client)
                return True
    return False


async def handle_console_inventory_prompt(channel: TextChannel):

    async def send_message(view: View) -> Message:
        return await channel.send(
            consolebridge.CONSOLE_INVENTORY_MESSAGE,
            view=view
        )

    await consolebridge.construct_console_inventory_prompt(send_message)


async def handle_console_shop_generate_prompt(channel: TextChannel, client):

    async def send_message(view: View) -> Message:
        return await channel.send(
            consolebridge.CONSOLE_SHOP_GENERATE_MESSAGE,
            view=view
        )

    await consolebridge.construct_console_shop_generate_prompt(send_message, client)


async def handle_console_change_status_prompt(channel: TextChannel, client):

    async def send_message(view: View) -> Message:
        return await channel.send(
            consolebridge.CONSOLE_CHANGE_CHARACTER_STATUS_MESSAGE,
            view=view
        )

    await consolebridge.construct_console_character_status_change_prompt(send_message, client)


async def handle_console_reinitialize(message, client):
    await consolebridge.reinitialize_console_messages(client)
    await message.delete()


async def handle_console_reserved_items_prompt(channel: TextChannel):

    async def send_message(view: View) -> Message:
        return await channel.send(
            consolebridge.CONSOLE_RESERVED_ITEM_MESSAGE,
            view=view
        )

    await consolebridge.construct_console_reserved_items_prompt(send_message)

