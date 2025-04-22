import asyncio
from datetime import datetime, timedelta

from api import magicshoprequests, channelsrequests
from controller import magicshop
from util import utils

DEFAULT_AUTO_SHOP_CHECK_INTERVAL = 60 * 60  # One hour.


async def post_magic_shop(shop_channel, character_levels_csv):
    new_shop_message = await shop_channel.send(magicshop.generate_new_magic_shop(character_levels_csv))
    channelsrequests.set_shop_message_id(new_shop_message.id)
    for index in range(1, magicshop.SHOP_MAX_NUMBER_OF_ITEMS + 1):
        await asyncio.sleep(5)
        await new_shop_message.add_reaction(utils.index_to_emoji(index))


async def post_shop_if_not_on_cooldown(shop_channel) -> float:
    last_date = magicshoprequests.get_magic_shop_last_date()
    next_interval = DEFAULT_AUTO_SHOP_CHECK_INTERVAL
    if last_date > 0:
        now_datetime = datetime.now()
        target_shop_weekday = -1
        for shop_weekday in magicshop.SHOP_WEEKDAYS_HOURS:
            if target_shop_weekday < shop_weekday <= now_datetime.weekday():
                target_shop_weekday = shop_weekday
        target_shop_datetime = now_datetime - timedelta(
            seconds=(now_datetime.weekday() - target_shop_weekday) * 24 * 60 * 60
        )
        target_shop_datetime = datetime(
            year=target_shop_datetime.year,
            month=target_shop_datetime.month,
            day=target_shop_datetime.day,
            hour=magicshop.SHOP_WEEKDAYS_HOURS[target_shop_weekday]
        )
        last_datetime = datetime.fromtimestamp(last_date)
        if target_shop_datetime > last_datetime:
            await post_magic_shop(shop_channel, magicshop.DEFAULT_SHOP_CHARACTER_LEVELS)
        else:
            next_interval = (last_datetime - target_shop_datetime).total_seconds()
    return next_interval


async def run_automatic_shop_posting(shop_channel):
    next_interval = await post_shop_if_not_on_cooldown(shop_channel)
    while True:
        await asyncio.sleep(next_interval)
        next_interval = await post_shop_if_not_on_cooldown(shop_channel)
