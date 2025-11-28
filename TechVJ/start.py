# TechVJ/start.py - Final Patch v3.0 (Fixed Imports)
import os
import asyncio 
import pyrogram
import time
import math
import glob 
import re
import asyncio.subprocess 
import logging
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserAlreadyParticipant, InviteHashExpired, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from .user_session import get_client 
# FIXED IMPORT: Import the module, not the variable directly
from TechVJ import user_session 

class batch_temp(object):
    IS_BATCH = {}

# --- HELPER FUNCTIONS ---

def humanbytes(size):
    if not size: return ""
    power = 2**10
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    n = 0
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}"

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((f"{days}d, " if days else "") + (f"{hours}h, " if hours else "") + (f"{minutes}m, " if minutes else "") + (f"{seconds}s, " if seconds else ""))
    if tmp.endswith(", "): tmp = tmp[:-2]
    if not tmp: return "0s"
    return tmp

async def split_file(file_path):
    try:
        await asyncio.sleep(2) 
        zip_base = file_path + ".zip"
        command = f'7z a -v1950m "{zip_base}" "{file_path}"'
        process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print(f"7z split failed: {stderr.decode()}")
            return []
        split_files = sorted(glob.glob(f"{zip_base}.*"))
        return split_files
    except Exception as e:
        print(f"Error in split_file: {e}")
        return []

def chunk_list(input_list, chunk_size):
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]

def get_message_type(msg):
    if msg.document: return "Document"
    if msg.video: return "Video"
    if msg.animation: return "Animation"
    if msg.sticker: return "Sticker"
    if msg.voice: return "Voice"
    if msg.audio: return "Audio"
    if msg.photo: return "Photo"
    if msg.text: return "Text"
    return None

def parse_link(link_text):
    private_pattern = r"https://t\.me/c/(\d+)/(\d+)(?:/(\d+))?"
    public_pattern = r"https://t\.me/([a-zA-Z0-9_]+)/(\d+)"
    link_text = link_text.replace("?single", "")
    
    match = re.search(private_pattern, link_text)
    if match:
        chat_id = int("-100" + match.group(1))
        msg_id_part = match.group(3) if match.group(3) else match.group(2)
        return chat_id, msg_id_part

    match = re.search(public_pattern, link_text)
    if match:
        return match.group(1), match.group(2)
    return None, None

async def progress_bar(current, total, client, message, start, type, file_name, processed_msgs, total_msgs):
    now = time.time()
    diff = now - start
    if round(diff % 8) == 0 or current == total:
        percentage = (current * 100) / total
        speed = current / diff if diff else 0
        eta = round((total - current) / speed) if speed else 0
        filled = "▪️"
        empty = "▫️"
        bar = "".join([filled for _ in range(math.floor(percentage / 10))]) + "".join([empty for _ in range(10 - math.floor(percentage / 10))])
        safe_file_name = file_name[:30] + "..." if len(file_name) > 30 else file_name
        stats = (f"📥 **Processing:** `{safe_file_name}`\n"
                 f"📊 **Progress:** `{percentage:.2f}%` [{bar}]\n"
                 f"📦 **Batch:** `{processed_msgs}/{total_msgs}`\n"
                 f"⚡ **Speed:** `{humanbytes(speed)}/s` | ⏳ **ETA:** `{TimeFormatter(eta * 1000)}`")
        try: await client.edit_message_text(message.chat.id, message.id, stats)
        except: pass

# --- BOT COMMANDS ---

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[InlineKeyboardButton("❣️ Developer", url = "https.t.me/kingvj01")],
               [InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
                InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')]]
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot.</b>", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(message.chat.id, "**Batch Successfully Cancelled.**")

# --- CORE LOGIC ---

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text):
        if LOGIN_SYSTEM: return await message.reply("Bot is in login mode. Join with your account.")
        if user_session.TechVJUser is None: return await client.send_message(message.chat.id, "String Session is not Set")
        try:
            await user_session.TechVJUser.join_chat(message.text)
            await client.send_message(message.chat.id, "Chat Joined")
        except UserAlreadyParticipant: await client.send_message(message.chat.id, "Chat already Joined")
        except Exception as e: await client.send_message(message.chat.id, f"Error : {e}")
        return

    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(user_id) == False:
            return await message.reply_text("**One Task Is Already Processing. /cancel it first.**")
        
        try:
            chatid, msg_part = parse_link(message.text)
            if chatid is None: return await message.reply_text("Invalid link format.")
            if "-" in msg_part:
                fromID = int(msg_part.split("-")[0].strip())
                toID = int(msg_part.split("-")[1].strip())
            else:
                fromID = int(msg_part.strip())
                toID = fromID
        except Exception as e: return await message.reply_text(f"Invalid format: {e}")

        acc = None
        if LOGIN_SYSTEM:
            acc = await get_client(user_id)
            if acc is None: return await message.reply("**You must /login first.**")
        else:
            # FIXED: Using user_session.TechVJUser instead of importing variable directly
            if user_session.TechVJUser is None:
                return await client.send_message(message.chat.id, f"**String Session is not Set**")
            acc = user_session.TechVJUser
        
        batch_temp.IS_BATCH[user_id] = False
        custom_chat_id = await db.get_destination_chat(user_id)
        chat_to_send = custom_chat_id or (int(CHANNEL_ID) if CHANNEL_ID else message.chat.id)
        message_ids = list(range(fromID, toID + 1))
        
        smsg = await client.send_message(message.chat.id, f"**Task:** `Starting...`\n**Total:** `{len(message_ids)}`")
        
        try:
            await handle_private_batch(client, acc, message, smsg, chat_to_send, chatid, message_ids)
        except Exception as e:
            await smsg.edit_text(f"**Error:** `{e}`")
        
        batch_temp.IS_BATCH[user_id] = True

async def handle_private_batch(client, acc, message, smsg, chat_to_send, chatid, message_ids):
    processed = 0
    total = len(message_ids)
    
    for chunk in chunk_list(message_ids, 100):
        if batch_temp.IS_BATCH.get(message.from_user.id): break
        
        chunk_msgs = []
        while True:
            try:
                chunk_msgs = await acc.get_messages(chatid, chunk)
                break
            except FloodWait as e:
                await smsg.edit_text(f"**FloodWait:** Sleeping {e.value}s...")
                await asyncio.sleep(e.value + 5)
                continue
            except Exception as e:
                if ERROR_MESSAGE: await smsg.edit_text(f"Error fetching: {e}")
                return

        for msg in chunk_msgs:
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            processed += 1
            if msg.empty: continue
            
            msg_type = get_message_type(msg)
            if not msg_type: continue
            
            if "Text" == msg_type:
                try: await client.send_message(chat_to_send, msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
                except: pass
                await asyncio.sleep(WAITING_TIME)
                continue

            file_name = "File"
            if msg.document: file_name = msg.document.file_name or "Document"
            elif msg.video: file_name = msg.video.file_name or "Video"
            elif msg.audio: file_name = msg.audio.file_name or "Audio"
            
            progress_args = [client, smsg, time.time(), "📥 Downloading", file_name, processed, total]
            f_path = None
            
            while True:
                try:
                    f_path = await acc.download_media(msg, progress=progress_bar, progress_args=progress_args)
                    break
                except FloodWait as e:
                    await smsg.edit_text(f"**Download FloodWait:** Sleeping {e.value}s...")
                    await asyncio.sleep(e.value + 5)
                except Exception: break
            
            if not f_path: continue
            if batch_temp.IS_BATCH.get(message.from_user.id):
                if os.path.exists(f_path): os.remove(f_path)
                break

            await smsg.edit_text(f"**📤 Uploading...**\nBatch: {processed}/{total}")
            
            files = [f_path]
            if os.path.getsize(f_path) > 1.95 * 1024**3:
                files = await split_file(f_path)
                os.remove(f_path)
            
            cap = msg.caption
            for i, fp in enumerate(files):
                if batch_temp.IS_BATCH.get(message.from_user.id):
                    if os.path.exists(fp): os.remove(fp)
                    break
                
                fname = os.path.basename(fp)
                new_cap = f"{fname}\nPart {i+1}/{len(files)}\n\n{cap}" if len(files)>1 else cap
                p_args = [client, smsg, time.time(), "📤 Uploading", fname, processed, total]
                
                while True:
                    try:
                        if len(files) > 1:
                            await client.send_document(chat_to_send, fp, caption=new_cap, progress=progress_bar, progress_args=p_args)
                        elif "Video" == msg_type:
                            await client.send_video(chat_to_send, fp, caption=new_cap, progress=progress_bar, progress_args=p_args)
                        elif "Audio" == msg_type:
                            await client.send_audio(chat_to_send, fp, caption=new_cap, progress=progress_bar, progress_args=p_args)
                        else:
                            await client.send_document(chat_to_send, fp, caption=new_cap, progress=progress_bar, progress_args=p_args)
                        break
                    except FloodWait as e:
                        await smsg.edit_text(f"**Upload FloodWait:** Sleeping {e.value}s...")
                        await asyncio.sleep(e.value + 5)
                    except Exception as e:
                        if ERROR_MESSAGE: await client.send_message(message.chat.id, f"Error up: {e}")
                        break
                
                if os.path.exists(fp): os.remove(fp)
            
            await asyncio.sleep(WAITING_TIME)

        if processed < total:
            await smsg.edit_text(f"**😴 Safety Sleep (30s)...**\nProcessed: {processed}/{total}")
            await asyncio.sleep(30)
            
    await smsg.delete()
    await client.send_message(message.chat.id, "**✅ Task Completed!**")