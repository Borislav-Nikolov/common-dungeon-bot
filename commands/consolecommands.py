from util import utils, botutils
from discord import TextChannel, Message
from discord.ui import View
from bridge import consolebridge


async def handle_console_commands(message) -> bool:
    console_key = '$console'
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] == console_key:
        # ADMIN COMMANDS
        if botutils.is_admin_message(message):
            if keywords[1] == 'inventory':
                await handle_console_inventory_prompt(message.channel)
                return True
    return False


async def handle_console_inventory_prompt(channel: TextChannel):

    async def send_message(view: View) -> Message:
        return await channel.send(
            consolebridge.CONSOLE_INVENTORY_MESSAGE,
            view=view
        )

    await consolebridge.construct_console_inventory_prompt(send_message)
