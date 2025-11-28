# TechVJ/user_session.py - Central Session Manager
import logging
from config import API_ID, API_HASH, STRING_SESSION, LOGIN_SYSTEM
from database.db import db
from pyrogram import Client

# Holds all dynamic user clients (for /login)
ACTIVE_CLIENTS = {}

# Holds the global static client (for STRING_SESSION)
TechVJUser = None

async def start_user_session():
    """Initializes the global string session client."""
    global TechVJUser
    if STRING_SESSION and not LOGIN_SYSTEM:
        try:
            TechVJUser = Client("TechVJ", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
            await TechVJUser.start() 
            logging.info("User session (TechVJUser) started.")
        except Exception as e:
            logging.error(f"Failed to start global user session: {e}")
            TechVJUser = None
    elif not LOGIN_SYSTEM:
        logging.warning("LOGIN_SYSTEM is False but STRING_SESSION is missing. Bot may not function.")

async def get_client(user_id: int) -> Client | None:
    """Gets a connected client from memory or DB."""
    client = ACTIVE_CLIENTS.get(user_id)
    if client:
        try:
            if not client.is_connected: await client.connect()
            return client
        except Exception as e:
            logging.warning(f"Client {user_id} re-connecting: {e}")

    session_string = await db.get_session(user_id)
    if not session_string: return None

    try:
        new_client = Client(f"user_session_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
        await new_client.connect()
        ACTIVE_CLIENTS[user_id] = new_client
        return new_client
    except Exception as e:
        logging.error(f"Failed to connect user {user_id}: {e}")
        await db.set_session(user_id, None)
        return None

async def add_client(user_id: int, client: Client):
    if user_id in ACTIVE_CLIENTS:
        try: await ACTIVE_CLIENTS[user_id].disconnect()
        except: pass
    ACTIVE_CLIENTS[user_id] = client

async def remove_client(user_id: int):
    if user_id in ACTIVE_CLIENTS:
        try: await ACTIVE_CLIENTS[user_id].disconnect()
        except: pass
        del ACTIVE_CLIENTS[user_id]
    await db.set_session(user_id, None)

async def disconnect_client_on_shutdown(user_id: int):
    if user_id in ACTIVE_CLIENTS:
        try: await ACTIVE_CLIENTS[user_id].disconnect()
        except: pass
        del ACTIVE_CLIENTS[user_id]

async def load_all_clients_from_db():
    logging.info("Loading all user sessions...")
    users = await db.get_all_users()
    async for user in users:
        uid, session = user.get('id'), user.get('session')
        if uid and session:
            try:
                client = Client(f"user_session_{uid}", api_id=API_ID, api_hash=API_HASH, session_string=session)
                await client.connect()
                ACTIVE_CLIENTS[uid] = client
            except Exception:
                await db.set_session(uid, None)