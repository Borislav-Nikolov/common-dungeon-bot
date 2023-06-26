import bot
import firebase
import os
from source import itemssource

from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    bot_token = str(os.getenv('TEST_TOKEN'))
    is_test = bot_token == str(os.getenv('TEST_TOKEN'))
    project_url = str(os.getenv('FIREBASE_PROJECT'))
    firebase.init_firebase(project_url, is_test)
    itemssource.init_items_source(is_test)
    bot.run_discord_bot(bot_token)
