# TechVJ/generate.py - Patched for session management
import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db
from .user_session import add_client, remove_client # <-- IMPORT NEW MANAGERS

SESSION_STRING_SIZE = 351 # A reasonable minimum length

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_id = message.from_user.id
    user_data = await db.get_session(user_id)  
    if user_data is None:
        return await message.reply("You are not logged in.")
        
    # This will disconnect the client, remove it from memory, and clear the DB
    await remove_client(user_id)
    
    await message.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_id = message.from_user.id
    user_data = await db.get_session(user_id)
    if user_data is not None:
        await message.reply("**You Are Already Logged In.**\nFirst, /logout your old session.")
        return 
    
    api_id = API_ID
    api_hash = API_HASH
    
    if not api_id or not api_hash:
        return await message.reply("`API_ID` and `API_HASH` are not set. Please contact the bot owner.")
        
    phone_number_msg = await bot.ask(chat_id=user_id, text="<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')
    phone_number = phone_number_msg.text
    
    # Use :memory: session_name to not create a file
    temp_client = Client(f"login_{user_id}", api_id, api_hash, in_memory=True)
    
    try:
        await temp_client.connect()
        await phone_number_msg.reply("Sending OTP...")
        code = await temp_client.send_code(phone_number)
        
        phone_code_msg = await bot.ask(user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \n\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n**Enter /cancel to cancel The Procces**", filters=filters.text, timeout=600)
    
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
        await temp_client.disconnect()
        return
    except TimeoutError:
        await phone_number_msg.reply('**Login timed out.**')
        await temp_client.disconnect()
        return
    except Exception as e:
        await phone_number_msg.reply(f"**Error:** `{e}`")
        await temp_client.disconnect()
        return

    if phone_code_msg.text == '/cancel':
        await temp_client.disconnect()
        return await phone_code_msg.reply('<b>Process cancelled!</b>')
    
    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await temp_client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**')
        await temp_client.disconnect()
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**')
        await temp_client.disconnect()
        return
    except SessionPasswordNeeded:
        two_step_msg = await bot.ask(user_id, '**Your account has enabled two-step verification. Please provide the password.\n\nEnter /cancel to cancel The Procces**', filters=filters.text, timeout=300)
        if two_step_msg.text == '/cancel':
            await temp_client.disconnect()
            return await two_step_msg.reply('<b>Process cancelled!</b>')
        try:
            password = two_step_msg.text
            await temp_client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid Password Provided**')
            await temp_client.disconnect()
            return
        except TimeoutError:
            await two_step_msg.reply('**Login timed out.**')
            await temp_client.disconnect()
            return
    except Exception as e:
        await phone_code_msg.reply(f"**Error:** `{e}`")
        await temp_client.disconnect()
        return

    # --- NEW SESSION HANDLING ---
    try:
        string_session = await temp_client.export_session_string()
        
        if len(string_session) < SESSION_STRING_SIZE:
            return await message.reply('<b>Error: Invalid session string generated.</b>')
        
        # 1. Save string to database
        await db.set_session(user_id, session=string_session)
        
        # 2. Add the *connected* client to the active pool
        # We rename the client's session name for our pool
        temp_client.session_name = f"user_session_{user_id}"
        await add_client(user_id, temp_client)
        
        await bot.send_message(user_id, "<b>Account Login Successfully.\nYou are now permanently connected.</b>")

    except Exception as e:
        await temp_client.disconnect()
        await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")
