from util import utils, botutils
from controller import magicshop, characters
from discord import Message
from bridge import charactersbridge
from model.item import Item


async def handle_magic_shop_reaction(payload, channel, client, shop_message):
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'
    info_emoji = '\U00002754'
    reserve_emoji = '\U0001F1F7'
    item_index = utils.emoji_to_index(str(payload.emoji))
    item_name = magicshop.get_item_name_by_index(item_index)
    dm_channel = await payload.member.create_dm()
    if item_name is None:
        if item_index == -1:
            await dm_channel.send('Item not found.')
        else:
            item_description = magicshop.get_shop_item_description(item_index)
            await dm_channel.send('That item has already been sold.')
            for description_part in item_description:
                await dm_channel.send(description_part)
        await shop_message.remove_reaction(payload.emoji, payload.member)
        raise Exception("Item not found in shop.")

    async def provide_message() -> Message:
        return await dm_channel.send(f'<@{payload.user_id}>, are you sure you want to buy **{item_name}**?\n'
                                     f'You can select the {info_emoji} to learn about the item.\n'
                                     f'Select the {reserve_emoji} to reserve the item for a future purchase.')

    async def on_emoji_click(clicked_emoji: str) -> bool:
        if clicked_emoji == accept_emoji:
            sold_item_name = magicshop.sell_item(payload.user_id, item_index)
            sold = len(sold_item_name) != 0
            if sold:
                shop_string = magicshop.get_current_shop_string()
                await shop_message.edit(content=shop_string)
                await charactersbridge.refresh_player_message(client, payload.user_id)
                await channel.send(magicshop.get_sold_item_string(payload.user_id, sold_item_name))
                if magicshop.get_item_name_by_index(item_index) is not None:
                    await shop_message.remove_reaction(payload.emoji, payload.member)
            else:
                await dm_channel.send(magicshop.get_failed_to_buy_item_string(payload.user_id, item_name))
                await shop_message.remove_reaction(payload.emoji, payload.member)
            return True
        elif clicked_emoji == decline_emoji:
            await dm_channel.send(f'Order of **{item_name}** was declined.')
            await shop_message.remove_reaction(payload.emoji, payload.member)
            return True
        elif clicked_emoji == info_emoji:
            item_description_info = magicshop.get_shop_item_description(item_index)
            for description_info_part in item_description_info:
                await dm_channel.send(description_info_part)
            return False
        elif clicked_emoji == reserve_emoji:
            reserved_item = characters.get_player_reserved_item(payload.user_id)
            if reserved_item is None:
                await set_reserved_item_and_send_messages(dm_channel, payload.user_id, item_index, item_name)
                await shop_message.remove_reaction(payload.emoji, payload.member)
                return True
            else:
                reserve_requested = await override_reserved_item_prompt(
                    client=client,
                    payload=payload,
                    dm_channel=dm_channel,
                    reserved_item=reserved_item,
                    new_item_name=item_name
                )
                if reserve_requested:
                    await set_reserved_item_and_send_messages(dm_channel, payload.user_id, item_index, item_name)
                    await shop_message.remove_reaction(payload.emoji, payload.member)
                    return True
                else:
                    await dm_channel.send(
                        f'Reservation of **{item_name}** canceled. You can still purchase via the above prompt.')
                    return False
        await dm_channel.send(f'An unexpected reaction was handled. Prompt canceled.')
        return True

    async def on_timeout():
        await dm_channel.send(f'Order of **{item_name}** has timed out.')
        await shop_message.remove_reaction(payload.emoji, payload.member)

    await botutils.create_emoji_prompt(
        client=client,
        user_id=payload.user_id,
        emoji_list=[accept_emoji, decline_emoji, info_emoji, reserve_emoji],
        prompt_message=provide_message,
        on_emoji_click=on_emoji_click,
        on_timeout=on_timeout
    )


async def set_reserved_item_and_send_messages(dm_channel, user_id, item_index, item_name):
    if not set_reserved_item(user_id, item_index):
        await dm_channel.send(f'There was an unexpected error: Item {item_name} not found. Aborting.')
    else:
        await dm_channel.send(f'You have successfully reserved **{item_name}**.')


def set_reserved_item(user_id, item_index) -> bool:
    shop_item = magicshop.get_shop_item(item_index)
    if shop_item is not None:
        characters.set_reserved_item(user_id, shop_item)
        return True
    else:
        return False


async def override_reserved_item_prompt(client, payload, dm_channel, reserved_item: Item, new_item_name) -> bool:
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'

    reserve_requested = False

    async def provide_message() -> Message:
        return await dm_channel.send(f'You already have **{reserved_item.name}** as a reserved item.\n'
                                     f'Would you like to override it with **{new_item_name}**?')

    async def on_emoji_click(clicked_emoji: str) -> bool:
        nonlocal reserve_requested
        if clicked_emoji == accept_emoji:
            reserve_requested = True
        return True

    async def on_timeout():
        await dm_channel.send(f'Reservation prompt for **{new_item_name}** has timed out.')

    await botutils.create_emoji_prompt(
        client=client,
        user_id=payload.user_id,
        emoji_list=[accept_emoji, decline_emoji],
        prompt_message=provide_message,
        on_emoji_click=on_emoji_click,
        on_timeout=on_timeout,
        timeout=15.0,
        timeout_after_interaction=20.0
    )

    return reserve_requested

