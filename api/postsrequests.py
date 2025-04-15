import requests
from api.base import api_url, get_bearer_token_headers


def get_posts(post_section_id) -> dict:
    url = api_url('get_posts')
    params = {'post_section_id': str(post_section_id)}
    response = requests.get(url, params=params, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return {}


def get_all_posts() -> dict:
    url = api_url('get_all_posts')
    response = requests.get(url, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return {}


def update_in_posts(posts_data) -> bool:
    url = api_url('update_in_posts')
    data = {'posts_data': posts_data}
    response = requests.post(url, json=data, headers=get_bearer_token_headers())
    return response.ok
