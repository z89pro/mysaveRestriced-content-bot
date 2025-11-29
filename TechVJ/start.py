# TechVJ/start.py - Final Version with Option 1 Design & Split Logic
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
    link_text = link_text.replace("?single", "").strip()
    try:
        if "t.me/c/" in link_text:
            parts = link_text.split("t.me/c/")[1].split("/")
            chat_id = int("-100" + parts[0])
            msg_part = parts[-1] 
            return chat_id, msg_part
        elif "t.me/" in link_text:
            parts = link_text.split("t.me/")[1].split("/")
            if len(parts) >= 2:
                return parts[0], parts[-1]
    except Exception as e:
        print(f"Parse Error: {e}")
    return None, None

# --- NEW PROGRESS BAR (OPTION 1 DESIGN) ---
async def progress_bar(current, total, client, message, start, type, file_name, processed_msgs, total_msgs, file_dc=None, user_dc=None):
    now = time.time()
    diff = now - start
    
    # Update every 8 seconds to avoid FloodWait
    if round(diff % 8) == 0 or current == total:
        percentage = (current * 100) / total
        speed = current / diff if diff else 0
        eta = round((total - current) / speed) if speed else 0
        elapsed = round(diff)
        
        # Circle Style Bar (12 Dots)
        filled = "●"
        empty = "○"
        bar_length = 12
        filled_length = math.floor((percentage / 100) * bar_length)
        bar = (filled * filled_length) + (empty * (bar_length - filled_length))
        
        # UpperCase Conversions for Design
        type_str = type.upper()
        name_str = file_name[:20].upper() + "..." if len(file_name) > 20 else file_name.upper()
        processed_size = humanbytes(current).upper()
        total_size = humanbytes(total).upper()
        speed_str = f"{humanbytes(speed)}/S".upper()
        eta_str = TimeFormatter(eta * 1000).upper()
        elapsed_str = TimeFormatter(elapsed * 1000).upper()
        file_dc_str = str(file_dc) if file_dc else "N/A"
        user_dc_str = str(user_dc) if user_dc else "N/A"

        # Final Stats String (Bold & Caps - Option 1)
        stats = (
            f"**TASK STATUS: {type_str} ({processed_msgs}/{total_msgs})**\n"
            f"**FILE NAME  : {name_str}**\n\n"
            f"**PROGRESS : [{bar}] {percentage:.2f}%**\n"
            f"**PROCESSED: {processed_size} OF {total_size}**\n"
            f"**SPEED    : {speed_str} | ETA: {eta_str}**\n"
            f"**DC ID    : {file_dc_str} (FILE) | {user_dc_str} (USER)**\n"
            f"**ELAPSED  : {elapsed_str}**"
        )
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
        except Exception as e: 
            return await message.reply_text(f"Invalid format or Link: {e}")

        acc = None
        if LOGIN_SYSTEM:
            acc = await get_client(user_id)
            if acc is None: return await message.reply("**You must /login first.**")
        else:
            if user_session.TechVJUser is None:
                return await client.send_message(message.chat.id, f"**String Session is not Set**")
            acc = user_session.TechVJUser
        
        batch_temp.IS_BATCH[user_id] = False
        custom_chat_id = await db.get_destination_chat(user_id)
        chat_to_send = custom_chat_id or (int(CHANNEL_ID) if CHANNEL_ID else message.chat.id)
        message_ids = list(range(fromID, toID + 1))
        
        smsg = await client.send_message(message.chat.id, f"**TASK:** `Starting...`\n**TOTAL:** `{len(message_ids)}`")
        
        try:
            await handle_private_batch(client, acc, message, smsg, chat_to_send, chatid, message_ids)
        except Exception as e:
            await smsg.edit_text(f"**Error:** `{e}`")
        
        batch_temp.IS_BATCH[user_id] = True

async def handle_private_batch(client, acc, message, smsg, chat_to_send, chatid, message_ids):
    processed = 0
    total = len(message_ids)
    
    # Extract User DC (from session)
    user_dc = None
    try: 
        if acc.session: user_dc = acc.session.dc_id
    except: pass

    for chunk in chunk_list(message_ids, 100):
        if batch_temp.IS_BATCH.get(message.from_user.id): break
        
        chunk_msgs = []
        while True:
            try:
                chunk_msgs = await acc.get_messages(chatid, chunk)
                break
            except FloodWait as e:
                await smsg.edit_text(f"**⚠️ FLOODWAIT DETECTED!**\n\nSleeping for {e.value}s...")
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
            file_dc = None
            
            # Extract File Metadata & DC
            if msg.document: 
                file_name = msg.document.file_name or "Document"
                file_dc = msg.document.dc_id
            elif msg.video: 
                file_name = msg.video.file_name or "Video"
                file_dc = msg.video.dc_id
            elif msg.audio: 
                file_name = msg.audio.file_name or "Audio"
                file_dc = msg.audio.dc_id
            elif msg.photo:
                file_name = "Photo.jpg"
                try: file_dc = msg.photo.file_id # Photos don't have direct DC ID like docs, placeholder
                except: pass
            
            # STATUS: DOWNLOADING
            progress_args = [client, smsg, time.time(), "DOWNLOADING", file_name, processed, total, file_dc, user_dc]
            f_path = None
            
            while True:
                try:
                    f_path = await acc.download_media(msg, progress=progress_bar, progress_args=progress_args)
                    break
                except FloodWait as e:
                    await smsg.edit_text(f"**⚠️ DOWNLOAD FLOODWAIT!**\nSleeping {e.value}s...")
                    await asyncio.sleep(e.value + 5)
                except Exception: break
            
            if not f_path: continue
            if batch_temp.IS_BATCH.get(message.from_user.id):
                if os.path.exists(f_path): os.remove(f_path)
                break
            
            # Extract Thumbnails & Metadata for Upload
            thumb_path = None
            duration = 0
            width = 0
            height = 0
            try:
                if msg.video:
                    duration, width, height = msg.video.duration, msg.video.width, msg.video.height
                    if msg.video.thumbs: thumb_path = await acc.download_media(msg.video.thumbs[0].file_id)
                elif msg.audio and msg.audio.thumbs: thumb_path = await acc.download_media(msg.audio.thumbs[0].file_id)
                elif msg.document and msg.document.thumbs: thumb_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except: pass
            
            # Split Logic Check (1.95 GB)
            files = [f_path]
            if os.path.getsize(f_path) > 1.95 * 1024**3:
                await smsg.edit_text(f"**⚠️ FILE > 2GB. SPLITTING...**")
                files = await split_file(f_path)
                os.remove(f_path)
            
            cap = msg.caption
            for i, fp in enumerate(files):
                if batch_temp.IS_BATCH.get(message.from_user.id):
                    if os.path.exists(fp): os.remove(fp)
                    break
                
                fname = os.path.basename(fp)
                new_cap = f"{fname}\nPart {i+1}/{len(files)}\n\n{cap}" if len(files)>1 else cap
                
                # STATUS: UPLOADING
                p_args = [client, smsg, time.time(), "UPLOADING", fname, processed, total, file_dc, user_dc]
                
                while True:
                    try:
                        if len(files) > 1:
                            await client.send_document(chat_to_send, fp, caption=new_cap, thumb=thumb_path, progress=progress_bar, progress_args=p_args)
                        elif "Video" == msg_type:
                            await client.send_video(chat_to_send, fp, caption=new_cap, duration=duration, width=width, height=height, thumb=thumb_path, progress=progress_bar, progress_args=p_args)
                        elif "Audio" == msg_type:
                            await client.send_audio(chat_to_send, fp, caption=new_cap, thumb=thumb_path, progress=progress_bar, progress_args=p_args)
                        elif "Voice" == msg_type:
                            await client.send_voice(chat_to_send, fp, caption=new_cap, progress=progress_bar, progress_args=p_args)
                        elif "Photo" == msg_type:
                            await client.send_photo(chat_to_send, fp, caption=new_cap, progress=progress_bar, progress_args=p_args)
                        else:
                            await client.send_document(chat_to_send, fp, caption=new_cap, thumb=thumb_path, progress=progress_bar, progress_args=p_args)
                        break
                    except FloodWait as e:
                        await smsg.edit_text(f"**⚠️ UPLOAD FLOODWAIT!**\nSleeping {e.value}s...")
                        await asyncio.sleep(e.value + 5)
                    except Exception as e:
                        if ERROR_MESSAGE: await client.send_message(message.chat.id, f"Error up: {e}")
                        break
                
                if os.path.exists(fp): os.remove(fp)
            
            if thumb_path and os.path.exists(thumb_path): os.remove(thumb_path)
            await asyncio.sleep(WAITING_TIME)

        if processed < total:
            await smsg.edit_text(f"**😴 SAFETY SLEEP (30S)...**\nProcessed: {processed}/{total}\nProtecting your Account.")
            await asyncio.sleep(30)
            
    await smsg.delete()
    await client.send_message(message.chat.id, "**✅ TASK COMPLETED!**")
