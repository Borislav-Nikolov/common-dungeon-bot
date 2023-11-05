import bot
import firebase
import os
from source import itemssource, magicshopsource, channelssource, playerssource, staticshopsource

from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    bot_token = str(os.getenv('TOKEN'))
    is_test = bot_token == str(os.getenv('TEST_TOKEN'))
    project_url = str(os.getenv('FIREBASE_PROJECT'))
    # initialize firebase realtime database components
    firebase.init_firebase(project_url)
    itemssource.init_items_source(is_test)
    magicshopsource.init_shop_source(is_test)
    channelssource.init_channels_source(is_test)
    playerssource.init_players_source(is_test)
    staticshopsource.init_static_shop_source(is_test)
    # start bot
    bot.run_discord_bot(bot_token)
