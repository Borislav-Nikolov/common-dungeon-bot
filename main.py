import bot
import firebase
import os

from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    bot_token = str(os.getenv('TOKEN'))
    is_test = bot_token == str(os.getenv('TEST_TOKEN'))
    firebase.init_firebase_refs(is_test)
    bot.run_discord_bot(bot_token)
