import requests
import api.base
from api.base import api_url


def chat_bogdy(prompt: str) -> str:
    url = api_url('chat_bogdy')
    data = {'prompt': prompt}
    response = requests.get(url, params=data, headers=api.base.get_bearer_token_headers())
    return response.json()['response']
