from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid, UserIdInvalid, UserNotParticipant, ChatInvalid
from database.db import db

# Helper function to check if bot is admin
async def is_bot_admin(client: Client, chat_id: int) -> bool:
    try:
        await client.get_chat_member(chat_id, "me")
        return True
    except (UserNotParticipant, ChatInvalid, PeerIdInvalid):
        return False
    except Exception:
        return False

@Client.on_message(filters.command(["settings"]))
async def settings_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    current_dest = await db.get_destination_chat(user_id)
    
    if current_dest:
        try:
            chat = await client.get_chat(current_dest)
            chat_name = chat.title or chat.first_name
            dest_text = f"**{chat_name}** (`{current_dest}`)"
        except Exception:
            dest_text = f"**Invalid Chat ID** (`{current_dest}`)\n\n*Please clear it using /clear_chat*"
    else:
        dest_text = "**Default** (Replies in this chat)"

    await message.reply_text(
        f"**⚙️ Your Current Settings**\n\n"
        f"📤 **Output Destination:** {dest_text}\n\n"
        f"Use `/set_chat CHAT_ID` to set a new destination.\n"
        f"Use `/clear_chat` to send back to the default chat."
    )

@Client.on_message(filters.command(["set_chat", "set_output"]))
async def set_chat_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text(
            "**Usage:** `/set_chat CHAT_ID`\n\n"
            "You can get the chat ID from a channel/group by forwarding a message from it to @RawDataBot.\n"
            "Use a **negative** ID for groups/channels (e.g., `-100123456`)."
        )
    
    try:
        chat_id_str = args[1]
        if not chat_id_str.startswith(("-", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0")):
             return await message.reply_text("Invalid Chat ID. It must be a numeric ID (e.g., `-100123456` or `123456789`).")
        
        chat_id = int(chat_id_str)
    except ValueError:
        return await message.reply_text("Invalid Chat ID. It must be a numeric ID (e.g., `-100123456`).")

    # Test the chat ID
    try:
        chat = await client.get_chat(chat_id)
        chat_name = chat.title or chat.first_name
        
        # Test if bot is in the chat
        if not await is_bot_admin(client, chat_id):
             await message.reply_text(f"⚠️ **Warning:** I am not a member or admin in **{chat_name}** (`{chat_id}`).\n\n"
                                      f"I will *try* to send files there, but it will **fail** unless you add me to that chat and give me admin rights.")

        await db.set_destination_chat(user_id, chat_id)
        await message.reply_text(f"✅ **Success!**\n\nOutput destination set to **{chat_name}** (`{chat_id}`).")
        
    except (PeerIdInvalid, UserIdInvalid, ChatInvalid):
        await message.reply_text("❌ **Error:** Invalid Chat ID.\n\nI cannot find that user, group, or channel. Please check the ID.")
    except Exception as e:
        await message.reply_text(f"❌ **An unknown error occurred:** `{e}`")


@Client.on_message(filters.command(["clear_chat"]))
async def clear_chat_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    await db.set_destination_chat(user_id, None)
    await message.reply_text("✅ **Success!**\n\nOutput destination has been reset to default (will reply in this chat).")