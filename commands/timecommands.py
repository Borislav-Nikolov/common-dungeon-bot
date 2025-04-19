from api import abdatetimerequests
from datetime import datetime
from util import utils, timeutils
from typing import Optional
from model.abdatetime import AbDatetime


async def handle_time_commands(message) -> bool:
    command_key = "$time"
    keywords = utils.split_strip(str(utils.first_line(message.content)), '.')
    if keywords[0] != command_key:
        return False

    await handle_time_command(message, keywords[1] if len(keywords) > 1 else None)

    return True


async def handle_time_command(message, date_str: Optional[str]) -> bool:
    if date_str:
        date_and_time = utils.split_strip(date_str, ' ')
        if len(date_and_time) == 1:
            date = date_and_time[0]
            # expected format: '%Y-%m-%d'
            real_date = timeutils.parse_date_str(date)
        else:
            real_date = timeutils.parse_datetime_str(date_str)
    else:
        real_date = datetime.now()
    ab_time: AbDatetime = abdatetimerequests.convert_datetime_to_abdatetime(real_date)
    await message.channel.send(timeutils.get_ab_string(ab_time))
    return True
