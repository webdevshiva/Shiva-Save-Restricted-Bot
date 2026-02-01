# 🚀 Save Restricted Content Bot

<p align="center">
  <img src="" alt="Bot Logo" width="200">
  <br>
  <b>A High-Performance Telegram Bot to Save Restricted Content</b>
  <br>
  <i>Developed with ❤️ by <a href="@theprofessorreport_bot">SHIVA CHAUDHARY</a></i>
</p>

---

## ✨ Features

* **🔓 Bypass Restricted Content**: Effortlessly save media from channels where "Save Content" is disabled.
* **📦 Batch Support**: Download a range of messages by sending a single range link (e.g., `10-100`).
* **🔑 Session Login**: Integrated `/login` for accessing private restricted channels via Pyrogram sessions.
* **🛡️ Verification System**: Advanced 6-hour token system with **url shortner** integration.
* **🚫 Savage Bypass Protection**: Built-in 30-second logic to prevent users from skipping your shortener.
* **📝 Dynamic Captions**: Automate branding with tags: `{file_name}`, `{file_size}`, and `{file_caption}`.
* **⚙️ Smart Settings**: Interactive callback menu to manage thumbnails, captions, and redirect channels.
* **⚡ Blazing Fast**: Optimized downloading and uploading with real-time progress bars.

---

## 🛠 Deployment Guide

### 1. Mandatory Variables
Configure these in your `config.py` or Environment Variables:

| Variable | Description |
| :--- | :--- |
| `API_ID` | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Your Telegram API Hash |
| `BOT_TOKEN` | Your Bot Token from [@BotFather](https://t.me/BotFather) |
| `ADMINS` | Telegram User IDs of Admins (separated by spaces) |
| `DATABASE_URL` | Your MongoDB URI |

## 🎮 Commands & Usage

### 👤 User Commands

| Command | Description |
| --- | --- |
| `/start` | Check bot status and active verification session. |
| `/login` | Authenticate your account for private restricted channel access. |
| `/set_caption` | Set a custom caption template for all your files. |
| `/set_thumb` | Reply to any image with this command to set a permanent thumbnail. |
| `/set_chat` | Redirect all your saved files to a specific Telegram channel. |

### 👑 Admin Commands

| Command | Description |
| --- | --- |
| `/verify_on` | Enable the URL Shortener verification system for all users. |
| `/verify_off` | Disable the verification system (Free access mode). |
| `/set_shortener` | Update Shortener API (Usage: `/set_shortener shortenerurl shortnerapikey`). |
| `/verify_stats` | View current shortener configuration and bot statistics. |
| `/broadcast` | Send a global notification message to all bot users. |

---

## 🏷 Dynamic Caption Tags

Aap apne custom caption ko dynamic banane ke liye niche diye gaye tags ka use kar sakte hain:

* `{file_name}` : File ka asli naam insert karega.
* `{file_size}` : File ka size (MB/GB mein) dikhayega.
* `{file_caption}` : Source post ka original caption include karega.

**Example Usage:**

> `/set_caption <b>File Name:</b> {file_name} ⚡️ \n<b>Size:</b> {file_size}`

---

## 🤝 Credits & Support

| Role | Link |
| --- | --- |
| **Developer** | [SHIVA CHAUDHARY](https://www.google.com/search?q=https://github.com/webdevshiva) |
| **Library** | [Pyrogram v2.0+](https://github.com/pyrogram/pyrogram) |
| **Support** | [Telegram Support](@theprofessorreport_bot) |

---

## 📜 License

This project is licensed under the **MIT License**.

* Use this bot responsibly.
* The developer is **not responsible** for any misuse or copyright issues.
* We do not support or promote piracy.

---
