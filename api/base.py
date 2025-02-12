import os
from dotenv import load_dotenv
from api import sockets

load_dotenv()

API_ENDPOINT = "https://common-dnd-backend.fly.dev/"
API_ENDPOINT_TEST = "https://common-dnd-backend-test.fly.dev/"
TEST_API_ENDPOINT_LOCAL_8081 = "http://localhost:8081/"

global endpoint
global is_test


def init_api(test: bool, local: bool):
    global is_test
    is_test = test
    global endpoint
    endpoint = TEST_API_ENDPOINT_LOCAL_8081 if local else API_ENDPOINT_TEST if test else API_ENDPOINT
    sockets.sio.connect(endpoint)


def api_url(function_name: str) -> str:
    return f'{endpoint}{function_name}'


def get_secret() -> str:
    secret_key = 'BACKEND_SECRET' if not is_test else 'TEST_BACKEND_SECRET'
    return os.getenv(secret_key)


def get_bearer_token_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_secret()}",
        "Content-Type": "application/json"
    }
