# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, LOGIN_SYSTEM

if STRING_SESSION is not None and LOGIN_SYSTEM == False:
    devshivaUser = Client(
        "devshiva",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION
    )
    devshivaUser.start()
else:
    devshivaUser = None

class Bot(Client):

    def __init__(self):
        super().__init__(
            "devshiva login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="devshiva"),
            workers=150,
            sleep_threshold=5
        )

    async def start(self):
        await super().start()
        print('Bot Started Powered By ShivaBots')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

if __name__ == "__main__":
    bot = Bot()
    bot.run()

# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot
