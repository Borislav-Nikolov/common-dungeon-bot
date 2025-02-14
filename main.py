import api.base
import bot
import firebase
import os
from source import itemssource, magicshopsource, playerssource, staticshopsource, postssource, \
    consolesource, rolepermissionssourse

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
    playerssource.init_players_source(is_test)
    staticshopsource.init_static_shop_source(is_test)
    postssource.init_posts_source(is_test)
    consolesource.init_console_source(is_test)
    rolepermissionssourse.init_role_permissions_source(is_test)
    api.base.init_api(test=is_test, local=False)
    # start bot
    bot.run_discord_bot(bot_token=bot_token, allowed_guild_id=str(os.getenv('ALLOWED_GUILD_ID')))

