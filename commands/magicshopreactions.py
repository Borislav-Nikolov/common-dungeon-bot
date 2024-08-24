from util import utils, botutils
from controller import magicshop
from discord import Message
from bridge import charactersbridge


async def handle_magic_shop_reaction(payload, channel, client, shop_message):
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'
    info_emoji = '\U00002754'
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
                                     f'You can select the {info_emoji} to learn about the item.')

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
        await dm_channel.send(f'An unexpected reaction was handled. Prompt canceled.')
        return True

    async def on_timeout():
        await dm_channel.send(f'Order of **{item_name}** has timed out.')
        await shop_message.remove_reaction(payload.emoji, payload.member)

    await botutils.create_emoji_prompt(
        client=client,
        user_id=payload.user_id,
        emoji_list=[accept_emoji, decline_emoji, info_emoji],
        prompt_message=provide_message,
        on_emoji_click=on_emoji_click,
        on_timeout=on_timeout
    )
