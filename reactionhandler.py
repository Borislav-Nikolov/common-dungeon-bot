import asyncio
import magicshop
import utils
import characters


async def handle_magic_shop_reaction(payload, channel, client):
    shop_message = await channel.fetch_message(payload.message_id)
    accept_emoji = '\U00002705'
    decline_emoji = '\U0000274C'
    info_emoji = '\U00002754'
    item_index = utils.emoji_to_index(str(payload.emoji))
    item_name = magicshop.get_item_name_by_index(item_index)
    dm_channel = await payload.member.create_dm()
    if item_name is None:
        await dm_channel.send(
            'That item has already been sold.\n\n' + magicshop.get_shop_item_description(item_index)
        )
        await shop_message.remove_reaction(payload.emoji, payload.member)
        raise Exception("Item not found in shop.")

    bot_message = None

    def check_command_emoji(inner_payload):
        user_id = inner_payload.user_id
        emoji = inner_payload.emoji
        return user_id == payload.user_id and bot_message.id == inner_payload.message_id and (
                    str(emoji) == accept_emoji or str(emoji) == decline_emoji or str(emoji) == info_emoji)

    bot_message = await dm_channel.send(f'<@{payload.user_id}>, are you sure you want to buy **{item_name}**?\n'
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
                sold_item_name = magicshop.sell_item(payload.user_id, item_index)
                sold = len(sold_item_name) != 0
                if sold:
                    shop_string = magicshop.get_current_shop_string()
                    await shop_message.edit(content=shop_string)
                    await characters.refresh_player_message(client, payload.user_id)
                    await channel.send(magicshop.get_sold_item_string(payload.user_id, sold_item_name))
                    if magicshop.get_item_name_by_index(item_index) is not None:
                        await shop_message.remove_reaction(payload.emoji, payload.member)
                else:
                    await dm_channel.send(magicshop.get_failed_to_buy_item_string(payload.user_id, item_name))
                    await shop_message.remove_reaction(payload.emoji, payload.member)
            elif str(result_payload.emoji) == decline_emoji:
                await dm_channel.send(f'Order of **{item_name}** was declined.')
                await shop_message.remove_reaction(payload.emoji, payload.member)
            elif str(result_payload.emoji) == info_emoji:
                result_payload = None
                timeout = 300.0
                await dm_channel.send(magicshop.get_shop_item_description(item_index))
    except asyncio.TimeoutError:
        await dm_channel.send(f'Order of **{item_name}** has timed out.')
        await shop_message.remove_reaction(payload.emoji, payload.member)
