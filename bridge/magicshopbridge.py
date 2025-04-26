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
        last_datetime = datetime.fromtimestamp(last_date)

        ordered_weekdays_from_last: list[int] = list()
        # Order the weekdays in a list, starting with the last shop date's weekday.
        for weekday_count in range(7):
            ordered_weekdays_from_last.append((weekday_count + last_datetime.weekday()) % 7)

        next_shop_weekday = -1
        next_shop_weekday_count_from_last = 0
        # Find the next shop weekday and number of days between the last shop weekday and the next shop weekday.
        for weekday in ordered_weekdays_from_last:
            if ordered_weekdays_from_last[0] == weekday:
                continue
            next_shop_weekday_count_from_last += 1
            if weekday in magicshop.SHOP_WEEKDAYS_HOURS:
                next_shop_weekday = weekday
                break

        # If there was no weekday found after the last date's weekday, default to one week after.
        if next_shop_weekday == -1:
            next_shop_weekday = ordered_weekdays_from_last[0]
            next_shop_weekday_count_from_last = 7

        # Construct the next shop datetime from the last datetime plus the difference in days.
        next_shop_datetime = last_datetime + timedelta(days=next_shop_weekday_count_from_last)
        next_shop_datetime = datetime(
            year=next_shop_datetime.year,
            month=next_shop_datetime.month,
            day=next_shop_datetime.day,
            hour=magicshop.SHOP_WEEKDAYS_HOURS[next_shop_weekday]
        )

        # Post the shop if the next shop datetime has passed already.
        if datetime.now() >= next_shop_datetime:
            await post_magic_shop(shop_channel, magicshop.DEFAULT_SHOP_CHARACTER_LEVELS)
        else:
            # Else, set the next shop cooldown check to be after the time between now and the next shop date.
            next_interval = (next_shop_datetime - datetime.now()).total_seconds()

    return next_interval


async def run_automatic_shop_posting(shop_channel):
    next_interval = await post_shop_if_not_on_cooldown(shop_channel)
    while True:
        await asyncio.sleep(next_interval)
        next_interval = await post_shop_if_not_on_cooldown(shop_channel)
