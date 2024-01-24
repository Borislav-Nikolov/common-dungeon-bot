from provider import staticshopprovider, channelsprovider
from controller import staticshop, characters, magicshop
from util import itemutils, botutils
from discord import Message


async def handle_static_shop_reactions(payload, client, item_message):
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'
    info_emoji = '\U00002754'
    static_shop_item = staticshopprovider.get_static_shop_item(item_message.id)
    dm_channel = await payload.member.create_dm()
    general_shop_channel = client.get_channel(channelsprovider.get_shop_channel_id())

    async def provide_message() -> Message:
        return await dm_channel.send(
            f'<@{payload.user_id}>, are you sure you want to buy **{static_shop_item.name}**?\n'
            f'You can select the {info_emoji} to learn about the item.')

    async def on_emoji_click(clicked_emoji: str) -> bool:
        if clicked_emoji == accept_emoji:
            sold = staticshop.sell_item(payload.user_id, static_shop_item)
            if sold:
                await characters.refresh_player_message(client, payload.user_id)
                await general_shop_channel.send(magicshop.get_sold_item_string(payload.user_id, static_shop_item.name))
                await item_message.remove_reaction(payload.emoji, payload.member)
            else:
                await dm_channel.send(
                    magicshop.get_failed_to_buy_item_string(payload.user_id, static_shop_item.name))
            await item_message.remove_reaction(payload.emoji, payload.member)
            return True
        elif clicked_emoji == decline_emoji:
            await dm_channel.send(f'Order of **{static_shop_item.name}** was declined.')
            await item_message.remove_reaction(payload.emoji, payload.member)
            return True
        elif clicked_emoji == info_emoji:
            item_description = itemutils.get_shop_item_description(static_shop_item)
            for description_part in item_description:
                await dm_channel.send(description_part)
            return False
        await dm_channel.send(f'An unexpected reaction was handled. Prompt canceled.')
        return True

    async def on_timeout():
        await dm_channel.send(f'Order of **{static_shop_item.name}** has timed out.')
        await item_message.remove_reaction(payload.emoji, payload.member)

    await botutils.create_emoji_prompt(
        client=client,
        user_id=payload.user_id,
        emoji_list=[accept_emoji, decline_emoji, info_emoji],
        prompt_message=provide_message,
        on_emoji_click=on_emoji_click,
        on_timeout=on_timeout
    )
