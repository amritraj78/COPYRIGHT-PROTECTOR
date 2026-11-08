import asyncio
import re
import time
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import OWNER_ID, SUDO_USERS
from PROTECTOR import PROTECTOR as app
from PROTECTOR.helper.mongo import (
    add_served_chat,
    add_served_user,
    get_chat_settings,
    get_chat_whitelist,
    get_auth_users,
    record_violation,
)

# Admin cache: {chat_id: {user_id: timestamp}}
ADMIN_CACHE = {}
ADMIN_CACHE_TTL = 300  # 5 minutes

# Regex patterns for copyright & piracy detection
MAGNET_REGEX = re.compile(r"magnet:\?xt=urn:[a-z0-9]+:[a-z0-9]{32,40}", re.IGNORECASE)
TORRENT_EXT_REGEX = re.compile(r"\.(torrent|nzb|cbr|cbz)$", re.IGNORECASE)

PIRACY_KEYWORDS = [
    r"\bcamrip\b",
    r"\btelesync\b",
    r"\bhdcam\b",
    r"\bhdtc\b",
    r"\bleaked\s+movie\b",
    r"\bfull\s+movie\s+leak(ed)?\b",
    r"\bleaked\s+course\b",
    r"\bleaked\s+m3u8\b",
    r"\b1337x\b",
    r"\bthepiratebay\b",
    r"\btorrentgalaxy\b",
    r"\byts\.mx\b",
    r"\braveleaks\b",
]
PIRACY_REGEX = re.compile("|".join(PIRACY_KEYWORDS), re.IGNORECASE)

INVITE_LINK_REGEX = re.compile(
    r"(t\.me\/(joinchat\/|\+[a-zA-Z0-9_-]+)|telegram\.me\/(joinchat\/|\+[a-zA-Z0-9_-]+)|discord\.(gg|com\/invite)\/[a-zA-Z0-9_-]+)",
    re.IGNORECASE,
)


async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if a user is an admin or owner in the chat with caching."""
    if user_id == OWNER_ID or user_id in SUDO_USERS:
        return True

    now = time.time()
    chat_admins = ADMIN_CACHE.get(chat_id, {})
    if user_id in chat_admins:
        cached_time, is_adm = chat_admins[user_id]
        if now - cached_time < ADMIN_CACHE_TTL:
            return is_adm

    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_adm = member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        if chat_id not in ADMIN_CACHE:
            ADMIN_CACHE[chat_id] = {}
        ADMIN_CACHE[chat_id][user_id] = (now, is_adm)
        return is_adm
    except Exception:
        return False


async def is_user_immune(chat_id: int, user_id: int) -> bool:
    """Check if the user is exempt from all filters."""
    if not user_id:
        return False
    if user_id == OWNER_ID or user_id in SUDO_USERS:
        return True
    
    # Check global auth sudoers from database
    auth_users = await get_auth_users()
    if user_id in auth_users:
        return True

    # Check chat whitelist
    whitelist = await get_chat_whitelist(chat_id)
    if user_id in whitelist:
        return True

    # Check chat admin status
    return await is_admin(chat_id, user_id)


async def send_auto_delete_alert(chat_id: int, text: str, delay: int = 7):
    """Sends a warning message to the chat that deletes itself after a delay."""
    try:
        msg = await app.send_message(chat_id, text, disable_web_page_preview=True)
        await asyncio.sleep(delay)
        await msg.delete()
    except Exception:
        pass


def check_piracy_content(message: Message) -> bool:
    """Check if message contains piracy keywords, torrents, or magnet links."""
    text = (message.text or message.caption or "")
    if MAGNET_REGEX.search(text):
        return True
    if PIRACY_REGEX.search(text):
        return True

    # Check document/audio/video file names
    media = message.document or message.video or message.audio
    if media and getattr(media, "file_name", None):
        if TORRENT_EXT_REGEX.search(media.file_name):
            return True
        if PIRACY_REGEX.search(media.file_name):
            return True

    return False


@app.on_message(filters.group & ~filters.me, group=1)
async def protection_message_handler(_, message: Message):
    chat = message.chat
    if not chat:
        return

    # Auto-register chat and user in database
    await add_served_chat(chat.id)
    if message.from_user:
        await add_served_user(message.from_user.id)

    # Fetch settings for this chat
    settings = await get_chat_settings(chat.id)
    if not settings.get("protect_mode", True):
        return

    # Handle messages sent on behalf of a channel (anonymous channel sender)
    if message.sender_chat and message.sender_chat.id != chat.id:
        if settings.get("anti_channel", False):
            try:
                await message.delete()
                await record_violation(chat.id, "anti_channel")
                if settings.get("delete_alert", True):
                    await send_auto_delete_alert(
                        chat.id,
                        f"📢 <b>ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ:</b> Messages from channels are not allowed in this group."
                    )
            except Exception:
                pass
            return

    # User ID check & immunity
    user = message.from_user
    if not user:
        return

    if await is_user_immune(chat.id, user.id):
        return

    # 1. Anti-Forward Protection (DMCA & Copyright Safe)
    is_forwarded = bool(
        message.forward_date
        or message.forward_from
        or message.forward_from_chat
        or message.forward_sender_name
    )
    if is_forwarded and settings.get("anti_forward", True):
        try:
            await message.delete()
            await record_violation(chat.id, "anti_forward")
            if settings.get("delete_alert", True):
                await send_auto_delete_alert(
                    chat.id,
                    f"🛡️ {user.mention}, <b>ғᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ!</b>\n"
                    f"ғᴏʀᴡᴀʀᴅɪɴɢ ᴄᴏɴᴛᴇɴᴛ ɪs ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴄᴏᴘʏʀɪɢʜᴛ sᴛʀɪᴋᴇs."
                )
        except Exception:
            pass
        return

    # 2. Anti-Piracy & Torrent Protection
    if settings.get("anti_piracy", True) and check_piracy_content(message):
        try:
            await message.delete()
            await record_violation(chat.id, "anti_piracy")
            if settings.get("delete_alert", True):
                await send_auto_delete_alert(
                    chat.id,
                    f"🧲 {user.mention}, <b>ᴘɪʀᴀᴄʏ / ᴛᴏʀʀᴇɴᴛ ᴄᴏɴᴛᴇɴᴛ ᴅᴇʟᴇᴛᴇᴅ!</b>\n"
                    f"sʜᴀʀɪɴɢ ᴄᴏᴘʏʀɪɢʜᴛᴇᴅ ʟᴇᴀᴋs ᴏʀ ᴛᴏʀʀᴇɴᴛs ɪs sᴛʀɪᴄᴛʟʏ ғᴏʀʙɪᴅᴅᴇɴ."
                )
        except Exception:
            pass
        return

    # 3. Anti-Invite & Link Protection
    text = (message.text or message.caption or "")
    if settings.get("anti_links", True) and INVITE_LINK_REGEX.search(text):
        try:
            await message.delete()
            await record_violation(chat.id, "anti_links")
            if settings.get("delete_alert", True):
                await send_auto_delete_alert(
                    chat.id,
                    f"🔗 {user.mention}, <b>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ʟɪɴᴋ ᴅᴇʟᴇᴛᴇᴅ!</b>\n"
                    f"ɪɴᴠɪᴛᴇ ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ."
                )
        except Exception:
            pass
        return

    # 4. Long Spam Message Protection
    max_words = settings.get("max_msg_words", 150)
    if text and len(text.split()) > max_words:
        try:
            await message.delete()
            await record_violation(chat.id, "long_message")
            if settings.get("delete_alert", True):
                await send_auto_delete_alert(
                    chat.id,
                    f"📝 {user.mention}, <b>ᴍᴇssᴀɢᴇ ᴛᴏᴏ ʟᴏɴɢ!</b>\n"
                    f"ᴘʟᴇᴀsᴇ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴜɴᴅᴇʀ {max_words} ᴡᴏʀᴅs."
                )
        except Exception:
            pass
        return


@app.on_edited_message(filters.group & ~filters.me, group=2)
async def protection_edited_message_handler(_, edited_message: Message):
    chat = edited_message.chat
    user = edited_message.from_user
    if not chat or not user:
        return

    settings = await get_chat_settings(chat.id)
    if not settings.get("protect_mode", True) or not settings.get("anti_edited", True):
        return

    if await is_user_immune(chat.id, user.id):
        return

    text = (edited_message.text or edited_message.caption or "")
    max_edit_words = settings.get("max_edit_words", 30)

    # Check if edited text exceeds limit or contains links/piracy
    has_violation = False
    reason = "ᴇᴅɪᴛ ʟᴇɴɢᴛʜ ᴇxᴄᴇᴇᴅᴇᴅ"

    if text and len(text.split()) > max_edit_words:
        has_violation = True
    elif check_piracy_content(edited_message):
        has_violation = True
        reason = "ᴘɪʀᴀᴄʏ ᴄᴏɴᴛᴇɴᴛ ɪɴ ᴇᴅɪᴛ"
    elif settings.get("anti_links", True) and INVITE_LINK_REGEX.search(text):
        has_violation = True
        reason = "ɪɴᴠɪᴛᴇ ʟɪɴᴋ ɪɴ ᴇᴅɪᴛ"

    if has_violation:
        try:
            await edited_message.delete()
            await record_violation(chat.id, "anti_edited")
            if settings.get("delete_alert", True):
                await send_auto_delete_alert(
                    chat.id,
                    f"📝 {user.mention}, <b>ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ!</b> ({reason})\n"
                    f"ᴇᴅɪᴛɪɴɢ ᴍᴇssᴀɢᴇs ᴛᴏ ʙʏᴘᴀss ᴄᴏᴘʏʀɪɢʜᴛ sʜɪᴇʟᴅs ɪs ɴᴏᴛ ᴘᴇʀᴍɪᴛᴛᴇᴅ."
                )
        except Exception:
            pass
