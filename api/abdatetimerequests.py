import requests

import api.base
from api.base import api_url
from datetime import datetime
from model.abdatetime import AbDatetime


def convert_datetime_to_abdatetime(date: datetime) -> AbDatetime:
    url = api_url('convert_real_date_to_in_game_date')
    params = {
        'year': date.year,
        'month': date.month,
        'day': date.day,
        'hour': date.hour,
        'minute': date.minute,
        'second': date.second
    }
    response_json = requests.get(url, params=params, headers=api.base.get_bearer_token_headers()).json()
    return AbDatetime(
        year=response_json['year'],
        month=response_json['month'],
        day=response_json['day'],
        hour=response_json['hour'],
        minute=response_json['minute'],
        second=response_json['second']
    )
