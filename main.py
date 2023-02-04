import bot
import firebase


if __name__ == '__main__':
    firebase.init_firebase_items_refs()
    bot.run_discord_bot()
