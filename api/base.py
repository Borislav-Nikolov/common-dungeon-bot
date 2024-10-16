
API_ENDPOINT = "https://common-dnd-backend.fly.dev/"


def api_url(function_name: str) -> str:
    return f'{API_ENDPOINT}{function_name}'
