# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot

import os
import asyncio
import time
import requests
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery 
from pyrogram.errors import UserNotParticipant
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, WAITING_TIME, ADMINS, LOG_CHANNEL
from database.db import db
from devshiva.strings import HELP_TXT
from utils.progress import progress_for_pyrogram

# --- IMPORT YOUR LOGIN FUNCTION ---
from devshiva.generate import main as login_handler

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
        clean_base = url.replace("https://", "").replace("http://", "").strip("/")
        api_url = f"https://{clean_base}/api?api={api}&url={link}"
        response = requests.get(api_url, timeout=10).json()
        if response.get("status") == "success":
            return response.get("shortenedUrl")
        return link 
    except Exception as e:
        print(f"Shortener Error: {e}")
        return link

# --- NEW: FORCE SUBSCRIBE CHECK ---
async def check_fsub(client, message):
    # Change your channel ID/Username in config or here
    FSUB_CHANNEL = -100123456789 # Example ID
    try:
        user = await client.get_chat_member(FSUB_CHANNEL, message.from_user.id)
        if user.status == enums.ChatMemberStatus.BANNED:
            await message.reply_text("❌ You are banned from using this bot.")
            return False
    except UserNotParticipant:
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel 📢", url="https://t.me/devXvoid")]])
        await message.reply_text("<b>⚠️ Access Denied!</b>\n\nYou must join our updates channel to use this bot.", reply_markup=join_btn)
        return False
    except Exception:
        return True
    return True

# --- START COMMAND & VERIFICATION ---
@Client.on_message(filters.command(["start"]) & filters.private)
async def send_start(client: Client, message: Message):
    if not await check_fsub(client, message): return
    
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        if LOG_CHANNEL:
            log_text = (f"<b>🆕 New User Started Bot</b>\n\n<b>👤 Name:</b> {user_mention}\n"
                        f"<b>🆔 User ID:</b> <code>{user_id}</code>\n"
                        f"<b>📅 Date:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}")
            try: await client.send_message(LOG_CHANNEL, log_text)
            except: pass

    if len(message.command) > 1 and message.command[1].startswith("verify"):
        sent_time = last_link_gen.get(user_id, 0)
        if time.time() - sent_time < 30:
            btn = [[InlineKeyboardButton("Try Again 🔐", callback_data="gen_link")]]
            return await message.reply_text("<b>⚠️ Bypass Detected!</b>\n\nDon't try to be smart! 😎 Complete properly.", reply_markup=InlineKeyboardMarkup(btn))
        await db.verify_user(user_id)
        return await message.reply_text("<b>Verification Successful! ✅</b>\n\nYou now have unlimited access for 6 hours.")

    is_verified = await db.get_verify_status(user_id)
    welcome_img = "logo.png" 
    welcome_text = (
        f"<b>👋 Hi {message.from_user.mention}!</b>\n\n"
        "I am a powerful **Save Restricted Content Bot**.\n\n"
        "✨ <b>Features:</b>\n"
        "🚀 <i>Batch Downloads & Custom Thumbnails</i>\n"
        "📝 <i>Dynamic Captions with {file_name} & {file_size}</i>\n"
        f"{'✅ <b>You have active premium access!</b>' if is_verified else '🔓 <b>Unlimited Access for 6 Hours (After Verify)</b>'}"
    )

    buttons = [[InlineKeyboardButton("Help 🛠️", callback_data="help"), InlineKeyboardButton("Login 🔑", callback_data="login_process")],
               [InlineKeyboardButton("Settings ⚙️", callback_data="settings_menu")]]
    if not is_verified: buttons[1].append(InlineKeyboardButton("Verify Bot 🔓", callback_data="gen_link"))
    
    await message.reply_photo(photo=welcome_img, caption=welcome_text, reply_markup=InlineKeyboardMarkup(buttons))

# --- ADMIN: STATS & BROADCAST ---
@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def get_stats(client, message):
    users_count = await db.total_users_count()
    await message.reply_text(f"<b>📊 Current Stats:</b>\n\nTotal Users: <code>{users_count}</code>")

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("Reply to a message to broadcast.")
    b_msg = await message.reply_text("<b>🚀 Broadcast Started...</b>")
    users = await db.get_all_users()
    success, failed = 0, 0
    for user in users:
        try:
            await message.reply_to_message.copy(user['id'])
            success += 1
        except: failed += 1
    await b_msg.edit(f"<b>✅ Broadcast Completed!</b>\n\nSent: {success}\nFailed: {failed}")

# --- CALLBACKS ---
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    if query.data == "login_process":
        await query.message.delete()
        try: await login_handler(client, query.message)
        except Exception as e: print(f"Login Handler Error: {e}")
    elif query.data == "gen_link":
        config = await db.get_verify_config()
        if not config.get('is_on'): return await query.answer("Verification is disabled.", show_alert=True)
        s_url, s_api = config.get('url'), config.get('api')
        token_link = f"https://t.me/{client.me.username}?start=verify_{user_id}"
        short_link = get_shortlink(s_url, s_api, token_link)
        last_link_gen[user_id] = time.time()
        btn = [[InlineKeyboardButton("Open Verification Link 🔓", url=short_link)]]
        await query.message.edit_caption(caption="<b>🔐 Security Verification Required</b>", reply_markup=InlineKeyboardMarkup(btn))
    elif query.data == "settings_menu":
        settings_text = ("<b>⚙️ Bot Configuration & Help</b>\n\n"
                        "<b>1️⃣ Caption Tags:</b>\n• <code>{file_name}</code>, <code>{file_size}</code>, <code>{file_caption}</code>\n\n"
                        "<b>2️⃣ Formatting Styles (HTML):</b>\n• Bold, Italic, Hyperlinks supported.\n\n"
                        "<b>3️⃣ Commands:</b>\n• /set_caption, /set_thumb, /set_chat")
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
        return await message.reply("<b>Usage:</b> <code>/set_caption Your Text</code>")
    caption = message.text.split(None, 1)[1]
    await db.set_caption(message.from_user.id, caption)
    await message.reply("✅ **Custom Caption Saved!**")

# --- MAIN LOGIC ---
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text: return
    if not await check_fsub(client, message): return
    
    user_id = message.from_user.id
    config = await db.get_verify_config()
    if config.get('is_on') and not await db.get_verify_status(user_id):
        return await message.reply("Verify first!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Verify 🔓", callback_data="gen_link")]]))

    if batch_temp.IS_BATCH.get(user_id) == False:
        return await message.reply_text("❌ A task is already running.")

    datas = message.text.split("/")
    temp = datas[-1].replace("?single","").split("-")
    fromID = int(temp[0].strip())
    toID = int(temp[1].strip()) if len(temp) > 1 else fromID
    
    # --- #work LOGS ---
    total_files = (toID - fromID) + 1
    if LOG_CHANNEL:
        log_work = (f"<b>#work</b>\n\n<b>Username:</b> @{message.from_user.username or 'N/A'}\n"
                    f"<b>First Name:</b> {message.from_user.first_name}\n"
                    f"<b>Process:</b> {'Batch' if total_files > 1 else 'Single'}\n"
                    f"<b>Total Files:</b> <code>{total_files}</code>")
        try: await client.send_message(LOG_CHANNEL, log_work)
        except: pass

    is_private = "/c/" in message.text
    acc = None
    if is_private:
        user_data = await db.get_session(user_id)
        if not user_data: return await message.reply("❌ Login first.")
        try:
            acc = Client("saver", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
            await acc.connect()
        except: return await message.reply("❌ Session Expired.")
    else: acc = client

    batch_temp.IS_BATCH[user_id] = False
    for msgid in range(fromID, toID + 1):
        if batch_temp.IS_BATCH.get(user_id): break
        chatid = int("-100" + datas[4]) if is_private else datas[3]
        try: await handle_private(client, acc, message, chatid, msgid)
        except: pass
        await asyncio.sleep(WAITING_TIME)

    if is_private and acc: await acc.disconnect()
    batch_temp.IS_BATCH[user_id] = True
    await message.reply("✅ **Task Completed!**")

# --- MEDIA HANDLER ---
async def handle_private(client: Client, acc, message: Message, chatid, msgid: int):
    try: msg = await acc.get_messages(chatid, msgid)
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
    media_obj = getattr(msg, msg.media.value)
    f_name = getattr(media_obj, "file_name", "No Name")
    f_size = get_readable_file_size(getattr(media_obj, "file_size", 0))
    final_cap = custom_caption.replace("{file_name}", f_name).replace("{file_size}", f_size).replace("{file_caption}", msg.caption or "") if custom_caption else (msg.caption or "")

    file = None
    ph_path = None
    try:
        file = await acc.download_media(msg, progress=progress_for_pyrogram, progress_args=("📥 **Downloading...**", smsg, time.time()))
        ph_path = await client.download_media(custom_thumb) if custom_thumb else None
        
        common_args = {"chat_id": target_chat, "caption": final_cap, "parse_mode": enums.ParseMode.HTML, "progress": progress_for_pyrogram, "progress_args": ("📤 **Uploading...**", smsg, time.time())}
        if msg.document: await client.send_document(document=file, thumb=ph_path, **common_args)
        elif msg.video: await client.send_video(video=file, thumb=ph_path, **common_args)
        elif msg.photo: await client.send_photo(photo=file, caption=final_cap)
        elif msg.audio: await client.send_audio(audio=file, thumb=ph_path, **common_args)
    except Exception as e: await smsg.edit(f"❌ Error: {e}")
    finally:
        # --- ROBUST AUTO-CLEAN ---
        if file and os.path.exists(file): os.remove(file)
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)
        await smsg.delete()

# Don't Remove Credit 
# Ask Doubt on telegram @theprofessorreport_bot
