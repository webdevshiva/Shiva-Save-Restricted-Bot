# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot

import traceback
import asyncio
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
# Make sure LOG_CHANNEL is added to your config.py
from config import API_ID, API_HASH, ADMINS, LOG_CHANNEL 
from database.db import db

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return await message.reply("<b>You are not logged in!</b>")
    
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successful** ✅\n\nYou will no longer be able to access private content until you /login again.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    user_data = await db.get_session(user_id)
    if user_data is not None:
        await message.reply("<b>You are already logged in!</b>\n\nTo perform a new login, please /logout first.")
        return 

    await message.reply("<b>🔐 Starting Login Process...</b>\n\nYou will need to provide your API ID and API HASH. If you don't have them, you can /skip to use the default ones.")

    # --- Step 1: API ID ---
    api_id_msg = await bot.ask(user_id, "<b>1. Send your API ID:</b>\n\nType /cancel to abort.\nTap /skip to use default settings.", filters=filters.text)
    
    if api_id_msg.text == "/cancel":
        return await api_id_msg.reply("❌ Login Cancelled.")
    
    if api_id_msg.text == "/skip":
        u_api_id = API_ID
        u_api_hash = API_HASH
    else:
        try:
            u_api_id = int(api_id_msg.text)
        except ValueError:
            return await api_id_msg.reply("❌ API ID must be a number. Please start /login again.")
        
        api_hash_msg = await bot.ask(user_id, "<b>2. Now send your API HASH:</b>", filters=filters.text)
        if api_hash_msg.text == "/cancel":
            return await api_hash_msg.reply("❌ Login Cancelled.")
        u_api_hash = api_hash_msg.text
        
    # --- Step 3: Phone Number ---
    phone_number_msg = await bot.ask(user_id, "<b>3. Send your Phone Number (with Country Code):</b>\nExample: `+912025550123`", filters=filters.text)
    if phone_number_msg.text == "/cancel":
        return await phone_number_msg.reply("❌ Login Cancelled.")
    phone_number = phone_number_msg.text

    temp_client = Client(":memory:", api_id=u_api_id, api_hash=u_api_hash)
    await temp_client.connect()
    
    await phone_number_msg.reply("⏳ Sending OTP...")
    
    try:
        code = await temp_client.send_code(phone_number)
    except PhoneNumberInvalid:
        await phone_number_msg.reply("❌ Invalid Phone Number format.")
        return
    except Exception as e:
        await phone_number_msg.reply(f"❌ Error: {e}")
        return

    # --- Step 4: OTP ---
    otp_msg = await bot.ask(user_id, "<b>4. Send your OTP:</b>\n\nCheck Telegram app. Add spaces between numbers.\nExample: `1 2 3 4 5`", filters=filters.text, timeout=300)
    
    if otp_msg.text == "/cancel":
        return await otp_msg.reply("❌ Login Cancelled.")
    
    otp = otp_msg.text.replace(" ", "")

    try:
        await temp_client.sign_in(phone_number, code.phone_code_hash, otp)
    except PhoneCodeInvalid:
        return await otp_msg.reply("❌ Invalid OTP. Try /login again.")
    except PhoneCodeExpired:
        return await otp_msg.reply("❌ OTP expired.")
    except SessionPasswordNeeded:
        pwd_msg = await bot.ask(user_id, "<b>5. Send 2-Step Verification Password:</b>", filters=filters.text, timeout=300)
        if pwd_msg.text == "/cancel":
            return await pwd_msg.reply("❌ Login Cancelled.")
        try:
            await temp_client.check_password(password=pwd_msg.text)
        except PasswordHashInvalid:
            return await pwd_msg.reply("❌ Incorrect Password!")

    string_session = await temp_client.export_session_string()
    await temp_client.disconnect()
    
    try:
        await db.set_session(user_id, string_session)
        await db.set_api_id(user_id, u_api_id)
        await db.set_api_hash(user_id, u_api_hash)
        
        await bot.send_message(user_id, "<b>✅ Login Successful!</b>")

        # --- OPTIONAL LOG NOTIFICATION ---
        if LOG_CHANNEL:
            log_text = (
                "<b>🔔 New User Login</b>\n\n"
                f"<b>👤 Name:</b> {user_name}\n"
                f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
                f"<b>📱 Phone:</b> <code>{phone_number}</code>\n"
                f"<b>🔑 API ID:</b> <code>{u_api_id}</code>"
            )
            try:
                await bot.send_message(LOG_CHANNEL, log_text)
            except Exception as log_err:
                print(f"Log Error: {log_err}")

    except Exception as e:
        await bot.send_message(user_id, f"<b>❌ Database Error:</b> `{e}`")

# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot
