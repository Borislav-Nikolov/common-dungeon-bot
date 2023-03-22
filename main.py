import bot
import firebase
import os

from dotenv import load_dotenv

import spreadsheet

load_dotenv()

if __name__ == '__main__':
    # TODO revert when done with the items
    spreadsheet.write_items_from_spreadsheet()
    # bot_token = str(os.getenv('TEST_TOKEN'))
    # is_test = bot_token == str(os.getenv('TEST_TOKEN'))
    # firebase.init_firebase_refs(is_test)
    # bot.run_discord_bot(bot_token)
