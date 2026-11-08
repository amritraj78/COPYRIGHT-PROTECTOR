# 🛡️ COPYRIGHT & ANTI-LEAK PROTECTOR BOT v2.0

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Pyrogram-v2.0.106-green.svg" alt="Pyrogram">
  <img src="https://img.shields.io/badge/Database-MongoDB-brightgreen.svg" alt="MongoDB">
  <img src="https://img.shields.io/badge/Deploy-Koyeb%20%7C%20Render%20%7C%20Heroku-orange.svg" alt="Deploy">
  <img src="https://img.shields.io/badge/Status-Active%20%26%20Maintained-success.svg" alt="Status">
</p>

An advanced, high-performance Telegram bot designed to safeguard your groups and channels from **DMCA copyright strikes**, **illegal torrents & piracy leaks**, **unauthorized invite spam**, **edited message exploits**, and **anonymous channel impersonators**.

---

## ✨ Features

- 🛡️ **Anti-Forward Shield**: Automatically detects and deletes forwarded messages from other channels or users to prevent DMCA takedowns.
- 🧲 **Anti-Piracy & Torrent Detection**: Eliminates `.torrent`, `.nzb` files, magnet links, and common piracy release terms (`camrip`, `telesync`, `hdcam`, `leaked course`, etc.).
- 🔗 **Anti-Invite & Link Shield**: Blocks Telegram invite links (`t.me/+`, `t.me/joinchat`) and malicious URLs.
- 📝 **Anti-Edit Message Exploit**: Catches users trying to sneak in copyright content or spam links by editing their message after sending.
- 📢 **Anti-Channel Sender**: Blocks messages sent on behalf of external channels to avoid channel raids.
- ⚙️ **Interactive Admin Control Panel**: Admins can toggle individual shields in real-time via `/settings` using inline buttons.
- 🛡️ **Admin & Sudo Immunity**: Admins, owners, sudoers, and whitelisted members are automatically immune.
- 🔔 **Self-Cleaning Warnings**: Warning messages self-destruct after 7 seconds, keeping group chats clean.
- 🌐 **Built-in HTTP Health Server**: Integrates a lightweight `aiohttp` web server on port `8000` to pass health checks seamlessly on Koyeb, Render, and cloud containers.
- 📊 **Real-time Analytics**: Tracks protected groups, served users, and blocked violations in MongoDB.
- 📢 **Advanced Broadcasting**: Sudoers can broadcast text or forwarded media to all groups and users with `-pin`, `-pinloud`, and `-user` options.

---

## 🚀 One-Click Deployments

### 1. Deploy on Koyeb
[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/amritraj78/COPYRIGHT-PROTECTOR&branch=main&name=copyright-protector)

### 2. Deploy on Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/amritraj78/COPYRIGHT-PROTECTOR)

### 3. Deploy via Docker
```bash
docker build -t copyright-protector .
docker run -d --env-file .env --name protector -p 8000:8000 copyright-protector
```

---

## 🛠️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_ID` | Yes | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Yes | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Yes | Bot Token from [@BotFather](https://t.me/BotFather) |
| `BOT_USERNAME` | Yes | Username of your Telegram Bot (without @) |
| `OWNER_ID` | Yes | Telegram User ID of the bot owner |
| `MONGO_URL` | Yes | MongoDB Connection URI (Atlas or Local) |
| `LOGGER_ID` | Optional | Telegram Channel / Group ID for bot logs |
| `PORT` | Optional | HTTP Health server port (Default: `8000`) |

---

## 🎮 Commands

### 👥 For Everyone
- `/start` - Start the bot and get navigation menu.
- `/help` - View interactive help cards and feature details.
- `/ping` - Check bot response latency and system status.
- `/stats` - View global protection stats and metrics.

### ⚙️ Group Administrators
- `/settings` - Open the interactive group protection panel.
- `/protect on` - Enable all protection shields.
- `/protect off` - Temporarily disable protection shields.
- `/whitelist [reply/user_id]` - Whitelist a user (exempt from all filters).
- `/unwhitelist [reply/user_id]` - Remove a user from whitelist.
- `/whitelisted` - View list of whitelisted members in group.
- `/purge [reply]` - Delete messages between reply and command.

### 👑 Bot Owner & Sudo
- `/broadcast [text/reply]` - Broadcast message to all protected groups.
  - `-user` : Broadcast to all private users.
  - `-pin` : Pin message silently.
  - `-pinloud` : Pin message with notification.
  - `-nobot` : Broadcast only to users.
- `/auth <user_id>` - Grant global sudo privileges.
- `/unauth <user_id>` - Revoke global sudo privileges.
- `/listauth` - View all global sudoers.

---

## 📜 License
Distributed under the **Apache License 2.0**.
