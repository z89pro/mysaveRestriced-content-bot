# config.py
import os
from dotenv import load_dotenv

# load .env from project root
load_dotenv()

def to_bool(val, default=False):
    if val is None:
        return default
    s = str(val).strip().lower()
    return s in ("1","true","yes","y","t")

def to_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

# Login feature
LOGIN_SYSTEM = to_bool(os.getenv("LOGIN_SYSTEM", "True"))

if LOGIN_SYSTEM is False:
    STRING_SESSION = os.getenv("STRING_SESSION", "") or None
else:
    STRING_SESSION = None

# Bot token @Botfather
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Your API ID from my.telegram.org
API_ID = to_int(os.getenv("API_ID", "0"))

# Your API Hash from my.telegram.org
API_HASH = os.getenv("API_HASH", "").strip()

# Your Owner / Admin Id For Broadcast 
ADMINS = to_int(os.getenv("ADMINS", "0"))

# Channel Id (use -100 prefix for supergroups)
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()

# Mongodb Database Url
DB_URI = os.getenv("DB_URI", "")
DB_NAME = os.getenv("DB_NAME", "vjsavecontentbot")

# Others
# This is the user-defined sleep time between EVERY message
WAITING_TIME = to_int(os.getenv("WAITING_TIME", "30")) 

ERROR_MESSAGE = to_bool(os.getenv("ERROR_MESSAGE", "True"))