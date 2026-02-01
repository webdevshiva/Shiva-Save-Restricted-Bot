# (c) [YOUR_NAME/YOUR_BRAND]
import os

# --- Login Configuration ---
# Set True for individual user login, False to use a single global session
LOGIN_SYSTEM = bool(os.environ.get('LOGIN_SYSTEM', True)) 

if LOGIN_SYSTEM == False:
    # If login system is False, fill your telegram account session below 
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
else:
    STRING_SESSION = None

# --- Bot Credentials ---
# Get these from @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Get these from my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# --- Admin & Database ---
# Your User ID (Important for Admin Commands)
ADMINS = int(os.environ.get("ADMINS", "5298223577"))

# MongoDB URL (Keep this private)
DB_URI = os.environ.get("DB_URI", "") 
DB_NAME = os.environ.get("DB_NAME", "shivasavecontentbot")

# --- Verification & Shortener Settings ---
# Default settings (Inhe Admin commands se change kiya ja sakta hai)
SHORTENER_URL = os.environ.get("SHORTENER_URL", "") # Example site
SHORTENER_API = os.environ.get("SHORTENER_API", "") # Your Shortener API Key
VERIFY_EXPIRE = int(os.environ.get("VERIFY_EXPIRE", "21600")) # Default 6 Hours (in seconds)

# --- Other Settings ---
# Target Channel for files (Leave empty if not needed)
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

# Time delay between messages to avoid Telegram flood/ban
WAITING_TIME = int(os.environ.get("WAITING_TIME", "5")) 

# Error notifications in private chat
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
