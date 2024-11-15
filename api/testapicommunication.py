import requests

from api.base import api_url


def test_api_communication() -> bool:
    url = api_url('test_bot_communication')
    response = requests.get(url)
    return response.status_code == 200
