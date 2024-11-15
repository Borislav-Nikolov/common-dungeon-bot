from model.inventorymessage import InventoryMessage
from typing import Callable, Awaitable
from discord import Message
from util import utils
from controller import characters
from discord import NotFound
from provider import channelsprovider, charactersprovider
from ui.playerview import PlayerView
from discord.interactions import Interaction
import time


async def send_inventory_messages(member, inventory_strings: list[dict[int, str]],
                                  send_message: Callable[[str], Awaitable[Message]]):
    player_id = member.id
    inventory_messages: list[InventoryMessage] = list()
    for item_count_to_string in inventory_strings:
        item_count = utils.dict_first_key(item_count_to_string)
        beginning_index = 20 * len(inventory_messages) + 1
        inventory_string = item_count_to_string[item_count]
        inventory_message = await send_message(inventory_string)
        for index in range(1, item_count + 1):
            time.sleep(1)
            await inventory_message.add_reaction(utils.index_to_emoji(index))
        inventory_messages.append(
            InventoryMessage(beginning_index=beginning_index, message_id=inventory_message.id))
    characters.set_inventory_messages(player_id, inventory_messages)


async def send_reserved_item_message(member, item_string: str, send_message: Callable[[str], Awaitable[Message]]):
    buy_emoji = '\U00002705'
    info_emoji = '\U00002754'
    reserved_item_message = await send_message(
        'What would you like to do with:\n'
        f'{item_string}\n'
        f'Click {buy_emoji} to buy it.\n'
        f'Click {info_emoji} for the item description.'
    )
    await reserved_item_message.add_reaction(buy_emoji)
    await reserved_item_message.add_reaction(info_emoji)
    characters.set_reserved_item_message(member.id, reserved_item_message.id)


async def update_character_status(client, player_id, character_name: str, status: str) -> bool:
    if characters.update_character_status(player_id, character_name, status):
        await refresh_player_message(client, player_id)
        return True
    return False


async def refresh_player_message(client, player_id):
    players_channel = client.get_channel(channelsprovider.get_characters_info_channel_id())
    player_message_id = channelsprovider.get_player_message_id(player_id)
    try:
        player_message = await players_channel.fetch_message(player_message_id)
        await edit_player_message(player_message, player_id)
    except NotFound:
        print(f'Message for player ID {player_id} was not found.')


async def send_player_message(channel, player_id) -> Message:
    return await channel.send(
        characters.get_up_to_date_player_message(player_id),
        view=get_player_view(player_id)
    )


async def edit_player_message(player_message, player_id) -> Message:
    return await player_message.edit(
        content=characters.get_up_to_date_player_message(player_id),
        view=get_player_view(player_id)
    )


def get_player_view(player_id) -> PlayerView:

    async def on_view_details(interaction: Interaction):
        await interaction.response.defer()
        dm_channel = await interaction.user.create_dm()
        await dm_channel.send(characters.get_detailed_player_message(player_id))

    return PlayerView(
        on_view_details_click=on_view_details
    )


async def reinitialize_character_messages(client):
    all_players = charactersprovider.get_all_players()
    for player in all_players:
        await refresh_player_message(client, player.player_id)
        time.sleep(5)
    print('All available player messages have been initialized.')
