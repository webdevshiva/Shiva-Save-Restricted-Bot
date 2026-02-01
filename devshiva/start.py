# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot

import os
import asyncio
import time
import requests
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery 
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, WAITING_TIME, ADMINS
from database.db import db
from devshiva.strings import HELP_TXT
from utils.progress import progress_for_pyrogram

# Bypass detection storage
last_link_gen = {}

class batch_temp(object):
    IS_BATCH = {}

# --- HELPERS ---
def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None: return "0B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def get_shortlink(url, api, link):
    try:
        # Clean the URL to ensure correct API call for nowshort.com
        clean_base = url.replace("https://", "").replace("http://", "").strip("/")
        api_url = f"https://{clean_base}/api?api={api}&url={link}"
        
        response = requests.get(api_url, timeout=10).json()
        if response.get("status") == "success":
            return response.get("shortenedUrl")
        return link 
    except Exception as e:
        print(f"Shortener Error: {e}")
        return link

# --- START COMMAND & VERIFICATION ---
@Client.on_message(filters.command(["start"]) & filters.private)
async def send_start(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    # Verification Handle (Bypass Protection)
    if len(message.command) > 1 and message.command[1].startswith("verify"):
        sent_time = last_link_gen.get(user_id, 0)
        # 30 Seconds Savage Rule
        if time.time() - sent_time < 30:
            btn = [[InlineKeyboardButton("Try Again 🔐", callback_data="gen_link")]]
            return await message.reply_text(
                "<b>⚠️ Bypass Detected!</b>\n\nDon't try to be smart! 😎 You must complete all steps on the website. Please click the button below and verify properly.",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        await db.verify_user(user_id)
        return await message.reply_text("<b>Verification Successful! ✅</b>\n\nYou now have unlimited access for 6 hours. Enjoy!")

    # Check verification status to hide/show button
    is_verified = await db.get_verify_status(user_id)
    
    welcome_img = "https://i.ibb.co/dJ0gpJf1/photo-2025-06-16-12-07-05-7516517596376596504.jpg" 
    welcome_text = (
        f"<b>👋 Hi {message.from_user.mention}!</b>\n\n"
        "I am a powerful **Save Restricted Content Bot**.\n\n"
        "✨ <b>Features:</b>\n"
        "🚀 <i>Batch Downloads & Custom Thumbnails</i>\n"
        "📝 <i>Dynamic Captions with {file_name} & {file_size}</i>\n"
        f"{'✅ <b>You have active premium access!</b>' if is_verified else '🔓 <b>Unlimited Access for 6 Hours (After Verify)</b>'}"
    )

    # Button logic: Only show "Verify Bot" if not verified
    buttons = [
        [InlineKeyboardButton("Help 🛠️", callback_data="help"), InlineKeyboardButton("Login 🔑", callback_data="login_process")],
        [InlineKeyboardButton("Settings ⚙️", callback_data="settings_menu")]
    ]
    
    if not is_verified:
        buttons[1].append(InlineKeyboardButton("Verify Bot 🔓", callback_data="gen_link"))

    await message.reply_photo(photo=welcome_img, caption=welcome_text, reply_markup=InlineKeyboardMarkup(buttons))

# --- CALLBACKS ---
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    if query.data == "gen_link":
        config = await db.get_verify_config()
        if not config.get('is_on'):
            return await query.answer("Verification is currently disabled.", show_alert=True)
        
        s_url, s_api = config.get('url'), config.get('api')
        if not s_url or not s_api:
            return await query.answer("Shortener API not configured by Admin!", show_alert=True)
        
        # Deep link target
        token_link = f"https://t.me/{client.me.username}?start=verify_{user_id}"
        
        # Generating Shortened Link via nowshort.com API
        short_link = get_shortlink(s_url, s_api, token_link)
        
        # Save timestamp for bypass check
        last_link_gen[user_id] = time.time()
        
        btn = [[InlineKeyboardButton("Open Verification Link 🔓", url=short_link)]]
        await query.message.edit_caption(
            caption="<b>🔐 Security Verification Required</b>\n\nComplete the verification on our website to unlock 6 hours of premium access.",
            reply_markup=InlineKeyboardMarkup(btn)
        )
    
    elif query.data == "settings_menu":
        settings_text = (
            "<b>⚙️ Bot Configuration & Help</b>\n\n"
            "<b>1️⃣ Caption Tags:</b>\n"
            "• <code>{file_name}</code> - Original File Name\n"
            "• <code>{file_size}</code> - File Size (MB/GB)\n"
            "• <code>{file_caption}</code> - Original Caption\n\n"
            "<b>2️⃣ Formatting Styles (HTML):</b>\n"
            "• <code>&lt;b&gt;Bold&lt;/b&gt;</code>, <code>&lt;i&gt;Italic&lt;/i&gt;</code>\n"
            "• <code>&lt;blockquote&gt;Quote Box&lt;/blockquote&gt;</code>\n"
            "• <code>&lt;a href='url'&gt;Hyperlink&lt;/a&gt;</code>\n\n"
            "<b>3️⃣ Commands:</b>\n"
            "• /set_caption - Set custom caption\n"
            "• /set_thumb - Reply to photo to set it\n"
            "• /set_chat - Redirect files to channel"
        )
        await query.message.edit_caption(caption=settings_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back 🔙", callback_data="back_start")]]))

    elif query.data == "help":
        await query.message.edit_caption(caption=HELP_TXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back 🔙", callback_data="back_start")]]))
    
    elif query.data == "back_start":
        await query.message.delete()
        await send_start(client, query.message)

# --- CAPTION SETTING ---
@Client.on_message(filters.command("set_caption") & filters.private)
async def set_caption_cmd(client, message):
    if len(message.command) < 2:
        tips = (
            "<b>✨ How to set Custom Caption</b>\n\n"
            "<b>Usage:</b> <code>/set_caption Your Text Here</code>\n\n"
            "<b>Available Tags:</b>\n"
            "• <code>{file_name}</code>, <code>{file_size}</code>, <code>{file_caption}</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/set_caption &lt;b&gt;Title:&lt;/b&gt; {file_name}\nSize: {file_size}</code>"
        )
        return await message.reply(tips)
    caption = message.text.split(None, 1)[1]
    await db.set_caption(message.from_user.id, caption)
    await message.reply("✅ **Custom Caption Saved Successfully!**")

# --- MAIN LOGIC ---
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text: return
    user_id = message.from_user.id

    config = await db.get_verify_config()
    if config.get('is_on') and not await db.get_verify_status(user_id):
        return await message.reply("<b>Access Denied! ❌</b>\nYour token has expired. Please verify to get 6 hours of unlimited use.", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Verify Now 🔓", callback_data="gen_link")]]))

    if batch_temp.IS_BATCH.get(user_id) == False:
        return await message.reply_text("❌ A task is already running. Please /cancel it.")

    datas = message.text.split("/")
    temp = datas[-1].replace("?single","").split("-")
    fromID = int(temp[0].strip())
    toID = int(temp[1].strip()) if len(temp) > 1 else fromID
    is_private = "/c/" in message.text
    acc = None

    if is_private:
        user_data = await db.get_session(user_id)
        if not user_data: return await message.reply("❌ Private Link. Please /login first.")
        try:
            acc = Client("saver", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
            await acc.connect()
        except: return await message.reply("❌ Session Expired. /login again.")
    else: acc = client

    batch_temp.IS_BATCH[user_id] = False
    for msgid in range(fromID, toID + 1):
        if config.get('is_on') and not await db.get_verify_status(user_id):
            await message.reply("<b>⚠️ Batch Paused!</b> Your 6-hour access expired. Verify to resume.")
            break
        if batch_temp.IS_BATCH.get(user_id): break
        chatid = int("-100" + datas[4]) if is_private else datas[3]
        try:
            await handle_private(client, acc, message, chatid, msgid)
        except Exception as e:
            if ERROR_MESSAGE: await message.reply(f"❌ Error {msgid}: {e}")
        await asyncio.sleep(WAITING_TIME)

    if is_private and acc: await acc.disconnect()
    batch_temp.IS_BATCH[user_id] = True
    await message.reply("✅ **Task Completed!**")

# --- MEDIA HANDLER ---
async def handle_private(client: Client, acc, message: Message, chatid, msgid: int):
    try:
        msg = await acc.get_messages(chatid, msgid)
    except: return
    if not msg or msg.empty: return 
    
    user_id = message.from_user.id
    target_chat = await db.get_target_chat(user_id) or message.chat.id
    custom_caption = await db.get_caption(user_id)
    custom_thumb = await db.get_thumb(user_id)

    if not msg.media:
        if msg.text: await client.send_message(target_chat, msg.text, entities=msg.entities)
        return

    smsg = await client.send_message(message.chat.id, "⏳ **Processing Media...**")
    
    # Logic for Dynamic Tags
    media_obj = getattr(msg, msg.media.value)
    f_name = getattr(media_obj, "file_name", "No Name")
    f_size = get_readable_file_size(getattr(media_obj, "file_size", 0))
    f_cap = msg.caption if msg.caption else ""

    if custom_caption:
        final_cap = custom_caption.replace("{file_name}", f_name).replace("{file_size}", f_size).replace("{file_caption}", f_cap)
    else:
        final_cap = f_cap

    start_time = time.time()
    try:
        file = await acc.download_media(msg, progress=progress_for_pyrogram, progress_args=("📥 **Downloading...**", smsg, start_time))
    except Exception as e:
        return await smsg.edit(f"❌ Download Fail: {e}")

    ph_path = await client.download_media(custom_thumb) if custom_thumb else None
    
    start_time = time.time()
    try:
        common_args = {"chat_id": target_chat, "caption": final_cap, "parse_mode": enums.ParseMode.HTML, "progress": progress_for_pyrogram, "progress_args": ("📤 **Uploading...**", smsg, start_time)}
        if msg.document: await client.send_document(document=file, thumb=ph_path, **common_args)
        elif msg.video: await client.send_video(video=file, thumb=ph_path, **common_args)
        elif msg.photo: await client.send_photo(photo=file, caption=final_cap, parse_mode=enums.ParseMode.HTML)
        elif msg.audio: await client.send_audio(audio=file, thumb=ph_path, **common_args)
        elif msg.voice: await client.send_voice(voice=file, caption=final_cap, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await smsg.edit(f"❌ Upload Fail: {e}")

    if os.path.exists(file): os.remove(file)
    if ph_path and os.path.exists(ph_path): os.remove(ph_path)
    await smsg.delete()

# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot