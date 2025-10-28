import requests
from api.base import api_url, get_bearer_token_headers


def get_session_logs_range(start_timestamp: int, end_timestamp: int) -> dict:
    """
    Get session logs within a timestamp range.

    Args:
        start_timestamp: Unix timestamp for the start of the range
        end_timestamp: Unix timestamp for the end of the range

    Returns:
        Dictionary of logs with timestamps as keys, or empty dict if request fails
    """
    url = api_url('get_session_logs_range')
    params = {
        'start': start_timestamp,
        'end': end_timestamp
    }
    response = requests.get(url, params=params, headers=get_bearer_token_headers())
    if response.ok:
        return response.json()
    return {}
