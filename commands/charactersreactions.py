from util import utils, botutils
from controller import characters, magicshop
from discord import Message, HTTPException, Forbidden, NotFound
from api import channelsrequests
from model.inventorymessage import InventoryMessage
from bridge import charactersbridge
from util import itemutils


async def handle_inventory_reaction(payload, user, channel, client, inventory_message) -> bool:
    player_id = payload.user_id
    is_inventory_message = False
    for player_inventory_message in characters.get_inventory_messages(player_id):
        if inventory_message.id == player_inventory_message.message_id:
            is_inventory_message = True
    if not is_inventory_message:
        return False
    item_index_relative = utils.emoji_to_index(str(payload.emoji))
    if item_index_relative == -1:
        return True
    try:
        inventory_item = characters.get_inventory_item_by_reaction_index(
            item_index_relative, inventory_message.id, player_id)
    except ValueError:
        return True
    if inventory_item is None:
        await channel.send("Item was not found.")
        return True

    sell_emoji = '\U0001FA99'
    destroy_emoji = '\U0001F5D1'
    cancel_emoji = '\U0000274C'

    # confirmation prompt emojis
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'

    async def provide_message() -> Message:
        return await channel.send(f'<@{payload.user_id}>, what would you like to do with **{inventory_item.name}**?\n'
                                  f'You can sell it by clicking {sell_emoji}.\n'
                                  f'You can delete it by clicking {destroy_emoji}.\n')

    async def refresh_inventory_messages():
        inventory_strings: list[dict[int, str]] = characters.get_inventory_strings(player_id)
        inventory_messages: list[InventoryMessage] = characters.get_inventory_messages(player_id)
        # prevent any interactions with the messages while they are being updated
        characters.set_inventory_messages(player_id, list())
        all_existing_messages = list()
        remaining_messages = list()
        for existing_message in inventory_messages:
            existing_message_id = existing_message.message_id
            old_message = await channel.fetch_message(existing_message_id)
            all_existing_messages.append(old_message)

        if len(inventory_strings) <= 0:
            for to_delete_message in inventory_messages:
                to_delete_id = to_delete_message.message_id
                fetched_message = await channel.fetch_message(to_delete_id)
                await fetched_message.delete()
        elif len(inventory_strings) > len(inventory_messages):

            async def send_message(string):
                return await channel.send(string)

            await charactersbridge.send_inventory_messages(user, inventory_strings, send_message)
        elif len(inventory_strings) < len(inventory_messages):
            messages_to_delete_count = len(inventory_messages) - len(inventory_strings)
            sorted_all_existing_messages = sorted(all_existing_messages, key=lambda message: message.created_at)
            messages_to_be_deleted = sorted_all_existing_messages[-messages_to_delete_count:]
            for message_to_delete in messages_to_be_deleted:
                await message_to_delete.delete()
            remaining_messages = sorted_all_existing_messages[:-messages_to_delete_count]
        elif len(inventory_strings) == len(inventory_messages):
            remaining_messages = all_existing_messages

        if len(remaining_messages) > 0:
            for remaining_message in remaining_messages:
                reactions = remaining_message.reactions
                for reaction in reactions:
                    try:
                        await remaining_message.remove_reaction(reaction, client.user)
                    except NotFound:
                        continue
                    except Forbidden:
                        continue
                    except HTTPException:
                        continue
                    except TypeError:
                        continue

            edited_message_index = -1

            async def edit_message(string):
                nonlocal edited_message_index
                edited_message_index += 1
                return await remaining_messages[edited_message_index].edit(content=string)

            await charactersbridge.send_inventory_messages(user, inventory_strings, edit_message)

    async def on_timeout():
        await channel.send(f'**{inventory_item.name}** interaction has timed out.')

    async def on_emoji_click(clicked_emoji: str) -> bool:
        if clicked_emoji == sell_emoji:

            async def provide_sell_item_message() -> Message:
                return await channel.send(f'Sell {inventory_item.name}?')

            async def handle_sell(clicked_destroy_emoji: str) -> bool:
                if clicked_destroy_emoji == accept_emoji:
                    sold_item_name = characters.refund_item_by_index(player_id, inventory_item.index)
                    sold = len(sold_item_name) != 0
                    if sold:
                        shop_channel_id = channelsrequests.get_shop_channel_id()
                        shop_channel = client.get_channel(shop_channel_id)
                        await shop_channel.send(magicshop.get_refunded_item_string(player_id, sold_item_name))
                        await charactersbridge.refresh_player_message(client, player_id)
                        await refresh_inventory_messages()
                    else:
                        await channel.send("Item could not be sold.")
                elif clicked_destroy_emoji == decline_emoji:
                    await channel.send("Canceled item sell.")
                return True

            await botutils.create_emoji_prompt(
                client=client,
                user_id=payload.user_id,
                emoji_list=[accept_emoji, decline_emoji],
                prompt_message=provide_sell_item_message,
                on_emoji_click=handle_sell,
                on_timeout=on_timeout
            )
            return True
        elif clicked_emoji == destroy_emoji:

            async def provide_destroy_item_message() -> Message:
                return await channel.send(f'Destroy {inventory_item.name}?')

            async def handle_destroy(clicked_destroy_emoji: str) -> bool:
                if clicked_destroy_emoji == accept_emoji:
                    if characters.remove_item_by_index(player_id, inventory_item.index):
                        await channel.send(f"**{inventory_item.name}** was removed from your inventory.")
                        await refresh_inventory_messages()
                    else:
                        await channel.send("Item was not removed.")
                elif clicked_destroy_emoji == decline_emoji:
                    await channel.send("Canceled item destruction.")
                return True

            await botutils.create_emoji_prompt(
                client=client,
                user_id=payload.user_id,
                emoji_list=[accept_emoji, decline_emoji],
                prompt_message=provide_destroy_item_message,
                on_emoji_click=handle_destroy,
                on_timeout=on_timeout
            )
            return True
        elif clicked_emoji == cancel_emoji:
            await channel.send(f'Interaction with {inventory_item.name} canceled.')
            return True
        await channel.send(f'An unexpected reaction was handled. Prompt canceled.')
        return True

    await botutils.create_emoji_prompt(
        client=client,
        user_id=payload.user_id,
        emoji_list=[sell_emoji, destroy_emoji, cancel_emoji],
        prompt_message=provide_message,
        on_emoji_click=on_emoji_click,
        on_timeout=on_timeout,
        timeout=60.0
    )
    return True


async def handle_reserved_item_reaction(payload, user, channel, client, reserved_item_message) -> bool:
    player_id = payload.user_id
    is_reserved_item_message = False
    for player_inventory_message in characters.get_reserved_items_messages(player_id):
        if reserved_item_message.id == player_inventory_message.message_id:
            is_reserved_item_message = True
    if not is_reserved_item_message:
        return False

    # TODO: transfer to a general/global reference
    buy_emoji = '\U00002705'
    info_emoji = '\U00002754'

    clicked_emoji = str(payload.emoji)

    if clicked_emoji == buy_emoji:
        reserved_item = characters.get_player_reserved_item(player_id)
        if reserved_item:
            if magicshop.sell_item_general(player_id, reserved_item):
                characters.remove_reserved_item_and_message(player_id)
                await charactersbridge.refresh_player_message(client, payload.user_id)
                shop_channel_id = channelsrequests.get_shop_channel_id()
                shop_channel = client.get_channel(shop_channel_id)
                await shop_channel.send(magicshop.get_sold_item_string(payload.user_id, reserved_item.name))
            else:
                await channel.send(f"Failed to buy {reserved_item.name}. Check if you have enough tokens.")
    elif clicked_emoji == info_emoji:
        reserved_item = characters.get_player_reserved_item(player_id)
        item_description_info = itemutils.get_shop_item_description(reserved_item)
        for description_info_part in item_description_info:
            await channel.send(description_info_part)
    return True
