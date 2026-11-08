import logging
import time
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, BOT_USERNAME, OWNER_ID

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

boot = time.time()

BOT_ID = 0
BOT_NAME = "Copyright Protector"
BOT_USERNAME = BOT_USERNAME

PROTECTOR = Client(
    "PROTECTOR_SESSION",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)
