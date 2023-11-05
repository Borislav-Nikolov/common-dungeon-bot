from provider import staticshopprovider, channelsprovider
from controller import staticshop, characters, magicshop
from util import itemutils
import asyncio


# TODO: check for repetitions with random shop reactions code and merge
async def handle_static_shop_reactions(payload, channel, client):
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'
    info_emoji = '\U00002754'
    item_message = await channel.fetch_message(payload.message_id)
    static_shop_item = staticshopprovider.get_static_shop_item(item_message.id)
    dm_channel = await payload.member.create_dm()
    general_shop_channel = client.get_channel(channelsprovider.get_shop_channel_id())

    bot_message = None

    def check_command_emoji(inner_payload):
        user_id = inner_payload.user_id
        emoji = inner_payload.emoji
        return user_id == payload.user_id and bot_message.id == inner_payload.message_id and (
                    str(emoji) == accept_emoji or str(emoji) == decline_emoji or str(emoji) == info_emoji)

    bot_message = await dm_channel.send(f'<@{payload.user_id}>, are you sure you want to buy **{static_shop_item.name}**?\n'
                                        f'You can select the {info_emoji} to learn about the item.')
    await bot_message.add_reaction(accept_emoji)
    await bot_message.add_reaction(decline_emoji)
    await bot_message.add_reaction(info_emoji)
    try:
        result_payload = None
        timeout = 30.0
        while result_payload is None:
            result_payload = await client.wait_for('raw_reaction_add', timeout=timeout, check=check_command_emoji)
            if str(result_payload.emoji) == accept_emoji:
                sold = staticshop.sell_item(payload.user_id, static_shop_item)
                if sold:
                    await characters.refresh_player_message(client, payload.user_id)
                    await general_shop_channel.send(magicshop.get_sold_item_string(payload.user_id, static_shop_item.name))
                    await item_message.remove_reaction(payload.emoji, payload.member)
                else:
                    await dm_channel.send(
                        magicshop.get_failed_to_buy_item_string(payload.user_id, static_shop_item.name))
                await item_message.remove_reaction(payload.emoji, payload.member)
            elif str(result_payload.emoji) == decline_emoji:
                await dm_channel.send(f'Order of **{static_shop_item.name}** was declined.')
                await item_message.remove_reaction(payload.emoji, payload.member)
            elif str(result_payload.emoji) == info_emoji:
                result_payload = None
                timeout = 300.0
                item_description = itemutils.get_shop_item_description(static_shop_item)
                for description_part in item_description:
                    await dm_channel.send(description_part)
    except asyncio.TimeoutError:
        await dm_channel.send(f'Order of **{static_shop_item.name}** has timed out.')
        await item_message.remove_reaction(payload.emoji, payload.member)
