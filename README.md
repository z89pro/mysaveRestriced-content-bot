# 🌟ZAIN Professional Save Restricted Bot

*An Advanced Telegram Bot to Save Restricted Content (Text, Media, Files) from Private or Public Channels/Groups.*

**🔥 New Features v2.0:**
- **Topic Support:** Works with Forum/Topic links (`.../c/ID/TOPIC/MSG`).
- **Smart FloodWait:** Automatically sleeps and retries if Telegram limits are hit.
- **Dual Sleep System:** - User-defined wait between messages.
  - **Safety Sleep:** Force 30s rest every 100 messages to prevent bans.
- **24/7 Uptime:** Built-in web server to keep the bot running on free platforms (Koyeb/Render).
- **Large Batch Support:** Can process 10,000+ messages using chunk processing.

---

## 🛠 Config Variables

- `LOGIN_SYSTEM` : Set to `True`. This allows you to login via the bot using `/login`.
- `API_ID` & `API_HASH` : Get from [my.telegram.org](https://my.telegram.org).
- `BOT_TOKEN` : Get from [@BotFather](https://t.me/BotFather).
- `DB_URI` : Your MongoDB Connection String (must start with `mongodb+srv://`).
- `CHANNEL_ID` : ID of the channel where you want files sent (e.g., `-100xxxx`). The bot must be an Admin there.
- `ADMINS` : Your User ID (for broadcast/admin commands).
- `WAITING_TIME` : Time in seconds to wait **after every message**. Recommended: `30` or more to stay safe.
- `ERROR_MESSAGE` : `True` to see error logs in chat, `False` to hide them.

  
*********************Variable Name (Key)	Description (Value kya daalna hai)
API_ID	Telegram API ID (Numbers mein, e.g., 123456)
API_HASH	Telegram API Hash (Ye lamba code hota hai)
BOT_TOKEN	BotFather se mila hua Bot Token
ADMINS	Aapka numeric Telegram User ID (e.g., 123456789)
CHANNEL_ID	Jis channel pe files bhejni hain, uska ID (Starts with -100)
DB_URI	MongoDB Connection String (Start hona chahiye mongodb+srv:// se)
LOGIN_SYSTEM	Iski value True rakhein.
WAITING_TIME	30 (Ya jitna seconds aap wait karwana chahte hain)
ERROR_MESSAGE	True (Errors dekhne ke liye)
PORT	8000 (Ye zaroori hai taaki web server chal sake)*********************
---

## 🤖 Commands

- `/start` - Check if bot is alive.
- `/login` - Login with your Telegram account (Required to fetch private content).
- `/logout` - Logout your session.
- `/settings` - Configure where to send the files (Default channel or Custom).
- `/set_chat` - Set a custom destination for your files.
- `/cancel` - Stop the current batch task.
- `/broadcast` - Send a message to all bot users (Admin only).

---

## 📝 Usage Guide

### 1. Private Chats / Restricted Content
*First, use `/login` to connect your account.*

**Single Message:**
Send the link: `https://t.me/c/xxxx/100`

**Batch (Range) of Messages:**
Send the range: `https://t.me/c/xxxx/100-150`

**Topic/Forum Links (Supported!):**
`https://t.me/c/xxxx/TOPIC_ID/MSG_ID`
`https://t.me/c/xxxx/TOPIC_ID/100-150`

### 2. Public Chats
Just send the post link: `https://t.me/channelname/100`

### 3. Bot Chats
Send the link with `/b/`: `https://t.me/b/botusername/4321`

---

## 🚀 Deployment (Koyeb/Render)

This bot includes a `start.sh` script to run a fake web server, allowing it to stay online 24/7 on free tiers using a monitoring service.

1. **Deploy** using Dockerfile.
2. **Add Variables** (API_ID, BOT_TOKEN, DB_URI, etc.).
3. **Set Port:** `8000`.
4. **After Deploy:** Use **UptimeRobot** to ping your app URL every 5 minutes.

---

## ❤️ Credits
- **Base Logic:** [BipinKrish](https://github.com/bipinkrish)
- **Advanced Modifications:** [Tech VJ](https://github.com/VJBots)
