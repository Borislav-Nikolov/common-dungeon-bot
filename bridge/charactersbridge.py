from model.inventorymessage import InventoryMessage
from typing import Callable, Awaitable
from discord import Message
from util import utils
from controller import characters


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
            await inventory_message.add_reaction(utils.index_to_emoji(index))
        inventory_messages.append(
            InventoryMessage(beginning_index=beginning_index, message_id=inventory_message.id))
    characters.set_inventory_messages(player_id, inventory_messages)


async def update_character_status(client, member, character_name: str, status: str) -> bool:
    player_id = member.id
    if characters.update_character_status(player_id, character_name, status):
        await characters.refresh_player_message(client, player_id)
        return True
    return False
