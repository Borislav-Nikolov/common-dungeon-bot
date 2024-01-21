from ui.basicbutton import BasicButton
from discord.interactions import Interaction
from provider import consoleprovider
from typing import Callable, Awaitable
from commands import characterscommands
from discord import ButtonStyle, Message
from discord.ui import View


CONSOLE_INVENTORY_MESSAGE = 'I can show you your inventory in a private message.\n' \
                            'From there you can manage your items by selling or deleting them.'


async def construct_console_inventory_prompt(send_message: Callable[[View], Awaitable[Message]]):
    view = View()

    async def send_inventory(interaction: Interaction):
        return await characterscommands.handle_inventory_prompt(interaction.user)

    button = BasicButton(
        label='Manage inventory',
        style=ButtonStyle.primary,
        on_click=send_inventory
    )
    view.add_item(button)
    sent_message: Message = await send_message(view)
    consoleprovider.set_inventory_console_message_id(sent_message.id, sent_message.channel.id)


async def reinitialize_console_inventory_if_needed(client):
    old_console_inventory_message_id = consoleprovider.get_inventory_console_message_id()
    old_console_inventory_channel_id = consoleprovider.get_inventory_console_channel_id()
    if old_console_inventory_message_id is not None and old_console_inventory_channel_id is not None:
        console_inventory_channel = client.get_channel(int(old_console_inventory_channel_id))
        console_inventory_message: Message = await console_inventory_channel.fetch_message(
            old_console_inventory_message_id)

        async def edited_inventory_message(view: View) -> Message:
            return await console_inventory_message.edit(
                content=CONSOLE_INVENTORY_MESSAGE,
                view=view
            )

        await construct_console_inventory_prompt(edited_inventory_message)
