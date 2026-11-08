import logging
from config import MONGO_URL, OWNER_ID
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("PROTECTOR.mongo")

DEFAULT_SETTINGS = {
    "protect_mode": True,      # Master protection toggle
    "anti_forward": True,      # Block forwarded messages from channels/users (DMCA safe)
    "anti_piracy": True,       # Block torrent, magnet, camrip, pirated keyword files
    "anti_links": True,        # Block telegram invite links & spam links
    "anti_edited": True,       # Block long edited messages or spam edits
    "anti_channel": False,     # Block messages sent on behalf of channels
    "delete_alert": True,      # Send self-destructing warning alert to user
    "max_edit_words": 30,      # Max allowed words in edited messages
    "max_msg_words": 150       # Max allowed words in a single message
}

# In-memory fallbacks if MongoDB is unavailable
_memory_users = set()
_memory_chats = set()
_memory_settings = {}
_memory_whitelist = {}
_memory_auth = {OWNER_ID}
_memory_violations = 0

mongodb = None
chatsdb = None
usersdb = None
settingsdb = None
whitelistdb = None
authdb = None
violationsdb = None

try:
    if MONGO_URL:
        _client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        mongodb = _client.PROTECTOR_BOT
        chatsdb = mongodb.tgchatsdb
        usersdb = mongodb.tgusersdb
        settingsdb = mongodb.chatsettingsdb
        whitelistdb = mongodb.chatwhitelistdb
        authdb = mongodb.authusersdb
        violationsdb = mongodb.violationsdb
        logger.info("Connected to MongoDB successfully.")
    else:
        logger.warning("MONGO_URL not provided. Using in-memory database storage.")
except Exception as e:
    logger.error("Failed to connect to MongoDB: %s. Falling back to in-memory storage.", e)
    mongodb = None


# --- Users Management ---
async def is_served_user(user_id: int) -> bool:
    if usersdb is not None:
        try:
            return bool(await usersdb.find_one({"user_id": user_id}))
        except Exception:
            pass
    return user_id in _memory_users

async def get_served_users() -> list:
    if usersdb is not None:
        try:
            users_list = []
            async for user in usersdb.find({"user_id": {"$gt": 0}}):
                users_list.append(user)
            return users_list
        except Exception:
            pass
    return [{"user_id": uid} for uid in _memory_users]

async def add_served_user(user_id: int):
    _memory_users.add(user_id)
    if usersdb is not None:
        try:
            if not await is_served_user(user_id):
                await usersdb.insert_one({"user_id": user_id})
        except Exception as e:
            logger.error("Error adding served user: %s", e)


# --- Chats Management ---
async def is_served_chat(chat_id: int) -> bool:
    if chatsdb is not None:
        try:
            return bool(await chatsdb.find_one({"chat_id": chat_id}))
        except Exception:
            pass
    return chat_id in _memory_chats

async def get_served_chats() -> list:
    if chatsdb is not None:
        try:
            chats_list = []
            async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
                chats_list.append(chat)
            return chats_list
        except Exception:
            pass
    return [{"chat_id": cid} for cid in _memory_chats]

async def add_served_chat(chat_id: int):
    _memory_chats.add(chat_id)
    if chatsdb is not None:
        try:
            if not await is_served_chat(chat_id):
                await chatsdb.insert_one({"chat_id": chat_id})
        except Exception as e:
            logger.error("Error adding served chat: %s", e)

async def remove_served_chat(chat_id: int):
    _memory_chats.discard(chat_id)
    if chatsdb is not None:
        try:
            await chatsdb.delete_one({"chat_id": chat_id})
        except Exception as e:
            logger.error("Error removing served chat: %s", e)


# --- Chat Settings ---
async def get_chat_settings(chat_id: int) -> dict:
    settings = DEFAULT_SETTINGS.copy()
    if settingsdb is not None:
        try:
            doc = await settingsdb.find_one({"chat_id": chat_id})
            if doc and "settings" in doc:
                settings.update(doc["settings"])
                return settings
        except Exception as e:
            logger.error("Error getting chat settings: %s", e)
    if chat_id in _memory_settings:
        settings.update(_memory_settings[chat_id])
    return settings

async def set_chat_setting(chat_id: int, key: str, value):
    current = await get_chat_settings(chat_id)
    current[key] = value
    _memory_settings[chat_id] = current
    if settingsdb is not None:
        try:
            await settingsdb.update_one(
                {"chat_id": chat_id},
                {"$set": {"settings": current}},
                upsert=True
            )
        except Exception as e:
            logger.error("Error setting chat setting: %s", e)
    return current

async def toggle_chat_setting(chat_id: int, key: str) -> bool:
    current = await get_chat_settings(chat_id)
    new_val = not current.get(key, DEFAULT_SETTINGS.get(key, True))
    await set_chat_setting(chat_id, key, new_val)
    return new_val


# --- Chat Whitelist (Per-Chat Immunity) ---
async def get_chat_whitelist(chat_id: int) -> list:
    if whitelistdb is not None:
        try:
            doc = await whitelistdb.find_one({"chat_id": chat_id})
            if doc and "users" in doc:
                return doc["users"]
        except Exception as e:
            logger.error("Error getting whitelist: %s", e)
    return list(_memory_whitelist.get(chat_id, set()))

async def add_chat_whitelist(chat_id: int, user_id: int) -> bool:
    if chat_id not in _memory_whitelist:
        _memory_whitelist[chat_id] = set()
    _memory_whitelist[chat_id].add(user_id)
    if whitelistdb is not None:
        try:
            await whitelistdb.update_one(
                {"chat_id": chat_id},
                {"$addToSet": {"users": user_id}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error("Error adding whitelist user: %s", e)
    return True

async def remove_chat_whitelist(chat_id: int, user_id: int) -> bool:
    if chat_id in _memory_whitelist:
        _memory_whitelist[chat_id].discard(user_id)
    if whitelistdb is not None:
        try:
            await whitelistdb.update_one(
                {"chat_id": chat_id},
                {"$pull": {"users": user_id}}
            )
            return True
        except Exception as e:
            logger.error("Error removing whitelist user: %s", e)
    return True


# --- Global Authorized / Sudo Users ---
async def get_auth_users() -> list:
    users = {OWNER_ID} | _memory_auth
    if authdb is not None:
        try:
            async for doc in authdb.find({"user_id": {"$gt": 0}}):
                users.add(doc["user_id"])
        except Exception as e:
            logger.error("Error getting auth users: %s", e)
    return list(users)

async def add_auth_user(user_id: int) -> bool:
    _memory_auth.add(user_id)
    if authdb is not None:
        try:
            await authdb.update_one(
                {"user_id": user_id},
                {"$set": {"user_id": user_id}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error("Error adding auth user: %s", e)
    return True

async def remove_auth_user(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return False
    _memory_auth.discard(user_id)
    if authdb is not None:
        try:
            await authdb.delete_one({"user_id": user_id})
            return True
        except Exception as e:
            logger.error("Error removing auth user: %s", e)
    return True


# --- Violations & Stats ---
async def record_violation(chat_id: int, violation_type: str = "general"):
    global _memory_violations
    _memory_violations += 1
    if violationsdb is not None:
        try:
            await violationsdb.update_one(
                {"_id": "global_stats"},
                {"$inc": {"total_violations": 1, f"types.{violation_type}": 1}},
                upsert=True
            )
        except Exception as e:
            logger.error("Error recording violation: %s", e)

async def get_total_violations() -> int:
    if violationsdb is not None:
        try:
            doc = await violationsdb.find_one({"_id": "global_stats"})
            if doc and "total_violations" in doc:
                return doc["total_violations"]
        except Exception:
            pass
    return _memory_violations
