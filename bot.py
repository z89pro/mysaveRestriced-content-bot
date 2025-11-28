# bot.py - Clean Entry Point
import logging
import sys
import asyncio
from pyrogram import Client, idle 
from config import API_ID, API_HASH, BOT_TOKEN, LOGIN_SYSTEM

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from TechVJ.user_session import (
    load_all_clients_from_db, 
    start_user_session,
    ACTIVE_CLIENTS, 
    disconnect_client_on_shutdown
)
# We import the module to access the global TechVJUser variable later
from TechVJ import user_session 

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techvj_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=150,
            sleep_threshold=5
        )

    async def start(self):
        await super().start()
        logging.info("Bot Started Powered By @VJ_Bots")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped Bye")

async def main():
    bot = Bot() 

    try:
        # 1. Start the Global User Session (String Session)
        await start_user_session()

        # 2. Load Login System Users
        if LOGIN_SYSTEM:
            await load_all_clients_from_db()

        # 3. Start Bot
        await bot.start()
        logging.info("Bot is now online and running.")
        await idle()

    except Exception as e:
        logging.exception(f"Bot crashed: {e}")
    finally:
        logging.info("Stopping bot...")
        if bot.is_connected:
            await bot.stop()
        
        # Stop Global Session
        if user_session.TechVJUser and user_session.TechVJUser.is_connected:
            await user_session.TechVJUser.stop()
        
        # Stop All Logged-in Users
        if LOGIN_SYSTEM:
            logging.info("Disconnecting user sessions...")
            for user_id in list(ACTIVE_CLIENTS.keys()):
                await disconnect_client_on_shutdown(user_id)

if __name__ == "__main__":
    asyncio.run(main())