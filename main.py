import bot
import firebase
import os
from source import itemssource, magicshopsource, channelssource, playerssource, staticshopsource, postssource, \
    consolesource, rolepermissionssourse

from dotenv import load_dotenv
# TODO: check if I have it here by default or it was installed because it may need to be installed when deployed:
#  pip install requests
import requests
import threading
import time


def get_request_test():
    url = 'http://127.0.0.1:5000/data'
    response = requests.get(url)
    if response.status_code == 200:
        print("GET request successful.")
        print("Response:", response.json())
    else:
        print(f"GET request failed with status code {response.status_code}.")


def update_request_test():
    url = 'http://127.0.0.1:5000/update'
    response = requests.get(url)
    if response.status_code == 200:
        print("Update request successful!")
        print("Response:", response.json())
    else:
        print(f"Update request failed with status code {response.status_code}.")


def post_requests_test():
    url = 'http://127.0.0.1:5000/post'
    data = {"key": "value", "number": 123}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("POST request successful.")
        print("Response:", response.json())
    else:
        print(f"POST request failed with status code {response.status_code}.")


def stream_updates():
    response = requests.get('http://127.0.0.1:5000/stream', stream=True)
    for line in response.iter_lines():
        if line:
            print('Update:', line.decode('utf-8'))


def run_all_test_calls():
    get_request_test()
    post_requests_test()
    sse_thread = threading.Thread(target=stream_updates)
    sse_thread.daemon = True  # Make sure the thread exits when the main program does
    sse_thread.start()
    while True:
        update_request_test()
        time.sleep(5)


load_dotenv()

if __name__ == '__main__':
    run_all_test_calls()
    # bot_token = str(os.getenv('TOKEN'))
    # is_test = bot_token == str(os.getenv('TEST_TOKEN'))
    # project_url = str(os.getenv('FIREBASE_PROJECT'))
    # # initialize firebase realtime database components
    # firebase.init_firebase(project_url)
    # itemssource.init_items_source(is_test)
    # magicshopsource.init_shop_source(is_test)
    # channelssource.init_channels_source(is_test)
    # playerssource.init_players_source(is_test)
    # staticshopsource.init_static_shop_source(is_test)
    # postssource.init_posts_source(is_test)
    # consolesource.init_console_source(is_test)
    # rolepermissionssourse.init_role_permissions_source(is_test)
    # # start bot
    # bot.run_discord_bot(bot_token=bot_token, allowed_guild_id=str(os.getenv('ALLOWED_GUILD_ID')))

