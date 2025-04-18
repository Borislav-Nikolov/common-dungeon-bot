import api.base
import bot
import os

from dotenv import load_dotenv


load_dotenv()

if __name__ == '__main__':
    bot_token = str(os.getenv('TEST_TOKEN'))
    is_test = bot_token == str(os.getenv('TEST_TOKEN'))
    project_url = str(os.getenv('FIREBASE_PROJECT'))
    api.base.init_api(test=is_test, local=True)
    # start bot
    bot.run_discord_bot(bot_token=bot_token, allowed_guild_id=str(os.getenv('TEST_ALLOWED_GUILD_ID')))
