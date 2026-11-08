import os
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Telegram API credentials
API_ID = int(getenv("API_ID", "6435225"))
API_HASH = getenv("API_HASH", "4e984ea35f854762dcde906dce426c2d")

# Bot credentials
BOT_TOKEN = getenv("BOT_TOKEN", "9016461792:AAFtaMtQ0CJiBYOUyEwgM3ykOI6e3ka1HWI")
BOT_USERNAME = getenv("BOT_USERNAME", "protection_rebot")

# Owner & Logger
OWNER_ID = int(getenv("OWNER_ID", "5423666218"))
LOGGER_ID = int(getenv("LOGGER_ID", "-1002014167331"))

# Database
MONGO_URL = getenv("MONGO_URL") or getenv("MONGO_DB_URI") or "mongodb+srv://amrit:amritkaneki@cluster0.kxvt1qj.mongodb.net/"

# Web server port for Koyeb/Render health check
PORT = int(getenv("PORT", "8000"))

# Sudo & Dev Users
DEV_USERS = [5423666218, 7044783841, 7019293589, 6757745933]
if OWNER_ID not in DEV_USERS:
    DEV_USERS.append(OWNER_ID)

SUDOERS = filters.user(DEV_USERS)