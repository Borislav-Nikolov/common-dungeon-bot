from ui.basicbutton import BasicButton
from discord.interactions import Interaction
from provider import consoleprovider
from api import channelsrequests
from typing import Callable, Awaitable
from commands import characterscommands, magicshopcommands
from discord import ButtonStyle, Message
from discord.ui import View
from ui.basicmodal import BasicModal
from ui.characterstatusview import CharacterStatusView
from util import botutils
from bridge import charactersbridge


CONSOLE_INVENTORY_MESSAGE = 'I can show you your inventory in a private message.\n' \
                            'From there you can manage your items by selling or deleting them.'

CONSOLE_SHOP_GENERATE_MESSAGE = 'Generate a new magic shop.\n' \
                                'This command is only available to the **Admin Pantheon**, praise them.'

CONSOLE_CHANGE_CHARACTER_STATUS_MESSAGE = '### Character status change\n'\
                                          'Change the status of one of your characters.\n\n' \
                                          'Instructions:\n' \
                                          '1) Choose a status from the dropdown menu below.\n' \
                                          '2) Click on the button.\n' \
                                          '3) Input your character\'s name in the pop-up window and submit.'

CONSOLE_RESERVED_ITEM_MESSAGE = 'Manage your reserved item.'


async def reinitialize_console_messages(client):
    await reinitialize_console_inventory_if_needed(client)
    await reinitialize_console_shop_generate_if_needed(client)
    await reinitialize_character_status_change_if_needed(client)
    await reinitialize_console_reserved_items_if_needed(client)


async def construct_console_inventory_prompt(send_message: Callable[[View], Awaitable[Message]]):
    view = View(timeout=None)

    async def send_inventory(interaction: Interaction):
        await interaction.response.defer()
        return await characterscommands.handle_inventory_prompt(interaction.user)

    button = BasicButton(
        label='Manage inventory',
        style=ButtonStyle.primary,
        on_click=send_inventory
    )
    view.add_item(button)
    sent_message: Message = await send_message(view)
    consoleprovider.set_inventory_console_message_id(sent_message.id, sent_message.channel.id)


async def construct_console_shop_generate_prompt(send_message: Callable[[View], Awaitable[Message]], client):
    view = View(timeout=None)

    async def generate_shop(interaction: Interaction):
        if not botutils.is_admin(interaction.user):
            return await interaction.response.send_message("You're not an admin.", ephemeral=True)

        async def handle_input(modal_interaction: Interaction, levels_separated_by_comma: str):
            channel_id = channelsrequests.get_shop_channel_id()
            channel = client.get_channel(channel_id)
            await modal_interaction.response.defer()
            return await magicshopcommands.handle_generate(
                channel,
                levels_separated_by_comma
            )

        return await interaction.response.send_modal(
            BasicModal(
                title='Generate Magic Shop',
                input_label='Levels',
                input_placeholder='Levels separated by comma...',
                on_submit_callback=handle_input
            )
        )

    button = BasicButton(
        label='Generate shop',
        style=ButtonStyle.primary,
        on_click=generate_shop
    )
    view.add_item(button)
    sent_message: Message = await send_message(view)
    consoleprovider.set_shop_generate_console_message_id(sent_message.id, sent_message.channel.id)


async def construct_console_character_status_change_prompt(send_message: Callable[[View], Awaitable[Message]], client):
    async def handle_input(interaction: Interaction, character_name: str, character_status: str) -> bool:
        try:
            await charactersbridge.update_character_status(
                client=client,
                player_id=interaction.user.id,
                character_name=character_name,
                status=character_status
            )
            await interaction.response.defer()
            return True
        except ValueError:
            print(f'Character not found for character_name={character_name}, at character status change.')
            await interaction.response.send_message(f'Wrong character name: {character_name}', ephemeral=True)
            return False

    async def handle_error(interaction: Interaction):
        await interaction.response.defer()

    view = CharacterStatusView(on_submit_callback=handle_input, on_handle_error=handle_error)
    sent_message: Message = await send_message(view)
    consoleprovider.set_character_status_console_message_id(sent_message.id, sent_message.channel.id)


async def construct_console_reserved_items_prompt(send_message: Callable[[View], Awaitable[Message]]):
    view = View(timeout=None)

    async def send_reserved_items(interaction: Interaction):
        await interaction.response.defer()
        return await characterscommands.handle_reserved_item_prompt(interaction.user)

    button = BasicButton(
        label='Manage reserved item',
        style=ButtonStyle.primary,
        on_click=send_reserved_items
    )
    view.add_item(button)
    sent_message: Message = await send_message(view)
    consoleprovider.set_reserved_items_console_message_id(sent_message.id, sent_message.channel.id)


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


async def reinitialize_console_shop_generate_if_needed(client):
    old_console_shop_generate_message_id = consoleprovider.get_shop_generate_console_message_id()
    old_console_shop_generate_channel_id = consoleprovider.get_shop_generate_console_channel_id()
    if old_console_shop_generate_message_id is not None and old_console_shop_generate_channel_id is not None:
        console_shop_generate_channel = client.get_channel(int(old_console_shop_generate_channel_id))
        console_shop_generate_message: Message = await console_shop_generate_channel.fetch_message(
            old_console_shop_generate_message_id)

        async def edited_shop_generate_message(view: View) -> Message:
            return await console_shop_generate_message.edit(
                content=CONSOLE_SHOP_GENERATE_MESSAGE,
                view=view
            )

        await construct_console_shop_generate_prompt(edited_shop_generate_message, client)


async def reinitialize_character_status_change_if_needed(client):
    old_console_character_status_message_id = consoleprovider.get_character_status_console_message_id()
    old_console_character_status_channel_id = consoleprovider.get_character_status_console_channel_id()
    if old_console_character_status_message_id is not None and old_console_character_status_channel_id is not None:
        console_character_status_channel = client.get_channel(int(old_console_character_status_channel_id))
        console_character_status_message: Message = await console_character_status_channel.fetch_message(
            old_console_character_status_message_id)

        async def edited_character_status_message(view: View) -> Message:
            return await console_character_status_message.edit(
                content=CONSOLE_CHANGE_CHARACTER_STATUS_MESSAGE,
                view=view
            )

        await construct_console_character_status_change_prompt(edited_character_status_message, client)


async def reinitialize_console_reserved_items_if_needed(client):
    old_console_reserved_items_message_id = consoleprovider.get_reserved_items_console_message_id()
    old_console_reserved_items_channel_id = consoleprovider.get_reserved_items_console_channel_id()
    if old_console_reserved_items_message_id is not None and old_console_reserved_items_channel_id is not None:
        console_reserved_items_channel = client.get_channel(int(old_console_reserved_items_channel_id))
        console_reserved_items_message: Message = await console_reserved_items_channel.fetch_message(
            old_console_reserved_items_message_id)

        async def edited_inventory_message(view: View) -> Message:
            return await console_reserved_items_message.edit(
                content=CONSOLE_RESERVED_ITEM_MESSAGE,
                view=view
            )

        await construct_console_reserved_items_prompt(edited_inventory_message)
