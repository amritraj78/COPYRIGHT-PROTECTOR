from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID, SUDO_USERS, SUDOERS
from PROTECTOR import PROTECTOR as app
from PROTECTOR.helper.mongo import (
    add_chat_whitelist,
    remove_chat_whitelist,
    get_chat_whitelist,
    add_auth_user,
    remove_auth_user,
    get_auth_users,
)
from PROTECTOR.modules.protection import is_admin


@app.on_message(filters.command("whitelist") & filters.group)
async def whitelist_user_handler(_, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    if not await is_admin(chat.id, user.id):
        return await message.reply_text("❌ <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ!</b>")

    target_user_id = None
    target_mention = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user_id = message.reply_to_message.from_user.id
        target_mention = message.reply_to_message.from_user.mention
    elif len(message.command) >= 2:
        try:
            target_user_id = int(message.command[1])
            target_mention = f"<code>{target_user_id}</code>"
        except ValueError:
            return await message.reply_text("Usage: `/whitelist [reply to user or user_id]`")
    else:
        return await message.reply_text("Usage: `/whitelist [reply to user or user_id]`")

    await add_chat_whitelist(chat.id, target_user_id)
    await message.reply_text(
        f"✅ {target_mention} <b>ʜᴀs ʙᴇᴇɴ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!</b>\n"
        f"ᴛʜᴇʏ ᴀʀᴇ ɴᴏᴡ ᴇxᴇᴍᴘᴛ ғʀᴏᴍ ᴀʟʟ ᴄᴏᴘʏʀɪɢʜᴛ & sᴘᴀᴍ sʜɪᴇʟᴅs."
    )


@app.on_message(filters.command("unwhitelist") & filters.group)
async def unwhitelist_user_handler(_, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    if not await is_admin(chat.id, user.id):
        return await message.reply_text("❌ <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ!</b>")

    target_user_id = None
    target_mention = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user_id = message.reply_to_message.from_user.id
        target_mention = message.reply_to_message.from_user.mention
    elif len(message.command) >= 2:
        try:
            target_user_id = int(message.command[1])
            target_mention = f"<code>{target_user_id}</code>"
        except ValueError:
            return await message.reply_text("Usage: `/unwhitelist [reply to user or user_id]`")
    else:
        return await message.reply_text("Usage: `/unwhitelist [reply to user or user_id]`")

    await remove_chat_whitelist(chat.id, target_user_id)
    await message.reply_text(
        f"⚠️ {target_mention} <b>ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴡʜɪᴛᴇʟɪsᴛ!</b>"
    )


@app.on_message(filters.command("whitelisted") & filters.group)
async def list_whitelisted_handler(_, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    if not await is_admin(chat.id, user.id):
        return await message.reply_text("❌ <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ!</b>")

    whitelist = await get_chat_whitelist(chat.id)
    if not whitelist:
        return await message.reply_text("ℹ️ <b>ɴᴏ ᴜsᴇʀs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.</b>")

    users_text = "\n".join([f"• <code>{uid}</code>" for uid in whitelist])
    await message.reply_text(
        f"📋 <b>ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ:</b>\n\n{users_text}"
    )


@app.on_message(filters.command("purge") & filters.group)
async def purge_handler(_, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    if not await is_admin(chat.id, user.id):
        return await message.reply_text("❌ <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ!</b>")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to start purging from.")

    start_id = message.reply_to_message.id
    end_id = message.id
    msg_ids = list(range(start_id, end_id + 1))

    deleted = 0
    # Delete in batches of 100 (Telegram limit)
    for i in range(0, len(msg_ids), 100):
        batch = msg_ids[i:i + 100]
        try:
            await app.delete_messages(chat.id, batch)
            deleted += len(batch)
        except Exception:
            pass

    confirm = await app.send_message(chat.id, f"🧹 <b>ᴘᴜʀɢᴇᴅ {deleted} ᴍᴇssᴀɢᴇs.</b>")
    await confirm.delete()


# --- Global Sudo & Owner Authorization (Persisted in MongoDB) ---

@app.on_message(filters.command("auth") & SUDOERS)
async def auth_user_cmd(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/auth <user_id>`")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid User ID.")

    auth_users = await get_auth_users()
    if user_id in auth_users:
        return await message.reply_text(f"User <code>{user_id}</code> is already authorized.")

    await add_auth_user(user_id)
    await message.reply_text(f"✅ User <code>{user_id}</code> has been authorized globally.")


@app.on_message(filters.command("unauth") & filters.user(OWNER_ID))
async def unauth_user_cmd(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/unauth <user_id>`")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid User ID.")

    if user_id == OWNER_ID:
        return await message.reply_text("Cannot unauthorize the Bot Owner.")

    await remove_auth_user(user_id)
    await message.reply_text(f"⚠️ User <code>{user_id}</code> has been unauthorized globally.")


@app.on_message(filters.command("listauth") & SUDOERS)
async def list_auth_users_cmd(_, message: Message):
    auth_users = await get_auth_users()
    if not auth_users:
        return await message.reply_text("No authorized users found.")

    users_text = "\n".join([f"• <code>{uid}</code>" for uid in auth_users])
    await message.reply_text(f"👑 <b>ɢʟᴏʙᴀʟʟʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs:</b>\n\n{users_text}")
