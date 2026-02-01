# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot

from pyrogram import Client, filters
from config import ADMINS
from database.db import db

@Client.on_message(filters.command("verify_on") & filters.private & filters.user(ADMINS))
async def verify_on(client, message):
    """To turn ON the verification system"""
    await db.set_verify_status(True)
    await message.reply_text(
        "<b>Verification System: Turned ON ✅</b>\n\n"
        "Now users must verify via a shortener to get 6 hours of access."
    )

@Client.on_message(filters.command("verify_off") & filters.private & filters.user(ADMINS))
async def verify_off(client, message):
    """To turn OFF the verification system"""
    await db.set_verify_status(False)
    await message.reply_text(
        "<b>Verification System: Turned OFF ❌</b>\n\n"
        "Users can now use the bot without any shortener verification."
    )

@Client.on_message(filters.command("set_shortener") & filters.private & filters.user(ADMINS))
async def set_shortener(client, message):
    """To set a new shortener URL and API key"""
    if len(message.command) < 3:
        return await message.reply_text(
            "<b>❌ Incorrect Format!</b>\n\n"
            "Usage: `/set_shortener sitename.com api_key`"
        )
    
    url = message.command[1]
    api = message.command[2]
    
    await db.update_shortener(url, api)
    await message.reply_text(
        f"<b>✅ Shortener Updated Successfully!</b>\n\n"
        f"🌐 <b>Website:</b> `{url}`\n"
        f"🔑 <b>API Key:</b> `{api}`"
    )

@Client.on_message(filters.command("verify_stats") & filters.private & filters.user(ADMINS))
async def verify_stats(client, message):
    """To view current verification settings"""
    config = await db.get_verify_config()
    
    status = "Enabled ✅" if config.get('is_on') else "Disabled ❌"
    url = config.get('url', 'Not Set')
    api = config.get('api', 'Not Set')
    
    stats_text = (
        "<b>🛠️ Verification System Settings</b>\n\n"
        f"<b>Current Status:</b> {status}\n"
        f"<b>Shortener URL:</b> `{url}`\n"
        f"<b>Shortener API:</b> `{api}`\n\n"
        "💡 <i>To change these, use /set_shortener</i>"
    )
    
    await message.reply_text(stats_text)

@Client.on_message(filters.command("admin_help") & filters.private & filters.user(ADMINS))
async def admin_help(client, message):
    """Admin help command"""
    help_text = (
        "<b>👑 Admin Control Panel</b>\n\n"
        "1️⃣ /verify_on - Enable verification\n"
        "2️⃣ /verify_off - Disable verification\n"
        "3️⃣ /set_shortener [url] [api] - Update shortener\n"
        "4️⃣ /verify_stats - View current settings\n"
        "5️⃣ /broadcast - Broadcast to users (if available)"
    )
    await message.reply_text(help_text)
