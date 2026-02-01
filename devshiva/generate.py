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
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return await message.reply("Aap logged in nahi hain!")
    
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ✅\nAb aap private content access nahi kar payenge jab tak phir se /login na karein.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if already logged in
    user_data = await db.get_session(user_id)
    if user_data is not None:
        await message.reply("<b>Aap pehle se logged in hain!</b>\n\nNaya login karne ke liye pehle /logout karein.")
        return 

    await message.reply("<b>🔐 Login Process Shuru Ho Raha Hai...</b>\n\nAapko apna API ID aur API HASH dena hoga. Agar aapke paas nahi hai, toh aap /skip kar sakte hain.")

    # --- Step 1: API ID ---
    api_id_msg = await bot.ask(user_id, "<b>1. Apna API ID bhejein:</b>\n\nProcess cancel karne ke liye /cancel likhein.\nSkip karne ke liye /skip dabayein (Recommended for beginners).", filters=filters.text)
    
    if api_id_msg.text == "/cancel":
        return await api_id_msg.reply("❌ Login Cancelled.")
    
    if api_id_msg.text == "/skip":
        u_api_id = API_ID
        u_api_hash = API_HASH
    else:
        try:
            u_api_id = int(api_id_msg.text)
        except ValueError:
            return await api_id_msg.reply("❌ API ID sirf numbers mein honi chahiye. Phir se /login karein.")
        
        # --- Step 2: API HASH ---
        api_hash_msg = await bot.ask(user_id, "<b>2. Ab apna API HASH bhejein:</b>", filters=filters.text)
        if api_hash_msg.text == "/cancel":
            return await api_hash_msg.reply("❌ Login Cancelled.")
        u_api_hash = api_hash_msg.text
        
    # --- Step 3: Phone Number ---
    phone_number_msg = await bot.ask(user_id, "<b>3. Apna Phone Number bhejein (Country Code ke saath):</b>\nExample: `+919876543210`", filters=filters.text)
    if phone_number_msg.text == "/cancel":
        return await phone_number_msg.reply("❌ Login Cancelled.")
    phone_number = phone_number_msg.text

    # Start Pyrogram Client for Session Generation
    temp_client = Client(":memory:", api_id=u_api_id, api_hash=u_api_hash)
    await temp_client.connect()
    
    await phone_number_msg.reply("⏳ OTP bhej raha hoon...")
    
    try:
        code = await temp_client.send_code(phone_number)
    except PhoneNumberInvalid:
        await phone_number_msg.reply("❌ Ye Phone Number invalid hai. Sahi format use karein.")
        return
    except Exception as e:
        await phone_number_msg.reply(f"❌ Error: {e}")
        return

    # --- Step 4: OTP ---
    otp_msg = await bot.ask(user_id, "<b>4. OTP bhejein:</b>\n\nOfficial Telegram app mein check karein. OTP ke beech mein space hona zaruri hai.\nExample: `1 2 3 4 5`", filters=filters.text, timeout=300)
    
    if otp_msg.text == "/cancel":
        return await otp_msg.reply("❌ Login Cancelled.")
    
    otp = otp_msg.text.replace(" ", "")

    try:
        await temp_client.sign_in(phone_number, code.phone_code_hash, otp)
    except PhoneCodeInvalid:
        return await otp_msg.reply("❌ OTP galat hai. Phir se /login karein.")
    except PhoneCodeExpired:
        return await otp_msg.reply("❌ OTP expire ho gaya hai.")
    except SessionPasswordNeeded:
        # --- Step 5: 2FA Password ---
        pwd_msg = await bot.ask(user_id, "<b>5. 2-Step Verification Password bhejein:</b>\nAapke account par 2FA laga hai.", filters=filters.text, timeout=300)
        if pwd_msg.text == "/cancel":
            return await pwd_msg.reply("❌ Login Cancelled.")
        try:
            await temp_client.check_password(password=pwd_msg.text)
        except PasswordHashInvalid:
            return await pwd_msg.reply("❌ Galat Password! Login fail ho gaya.")

    # Export & Save Session
    string_session = await temp_client.export_session_string()
    await temp_client.disconnect()
    
    try:
        # Saving everything to DB (Calls updated db.py methods)
        await db.set_session(user_id, string_session)
        await db.set_api_id(user_id, u_api_id)
        await db.set_api_hash(user_id, u_api_hash)
        
        await bot.send_message(user_id, "<b>✅ Login Successful!</b>\n\nAb aap private channels ke links bhej sakte hain. Bot unhe automatically download kar lega.")
    except Exception as e:
        await bot.send_message(user_id, f"<b>❌ Error saving session:</b> `{e}`")

# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot