import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatWriteForbidden
from config import SUDOERS
from PROTECTOR import PROTECTOR as app
from PROTECTOR.helper.mongo import get_served_chats, get_served_users, remove_served_chat

IS_BROADCASTING = False


@app.on_message(filters.command(["broadcast", "gcast", "bcast"]) & SUDOERS)
async def broadcast_message(client, message):
    global IS_BROADCASTING

    if IS_BROADCASTING:
        return await message.reply_text("⚠️ <i>ᴀ ʙʀᴏᴀᴅᴄᴀsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss. ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>")

    # Check replied message or query text
    reply_msg = message.reply_to_message
    if not reply_msg and len(message.command) < 2:
        return await message.reply_text(
            "**📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴜsᴀɢᴇ:**\n\n"
            "• `/broadcast [text]`\n"
            "• `/broadcast [reply to any message/media]`\n\n"
            "**ғʟᴀɢs:**\n"
            "`-user` : Broadcast to all private bot users\n"
            "`-pin` : Pin message silently\n"
            "`-pinloud` : Pin message with notification\n"
            "`-nobot` : Skip group broadcasting"
        )

    query = ""
    if not reply_msg:
        query = message.text.split(None, 1)[1]
        for flag in ["-pin", "-nobot", "-pinloud", "-user"]:
            query = query.replace(flag, "")
        query = query.strip()
        if not query:
            return await message.reply_text("Please provide text to broadcast.")

    IS_BROADCASTING = True
    status_msg = await message.reply_text("🚀 <i>ɪɴɪᴛɪᴀʟɪᴢɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ...</i>")

    flags = message.text or ""
    pin_silent = "-pin" in flags
    pin_loud = "-pinloud" in flags
    to_users = "-user" in flags
    skip_groups = "-nobot" in flags

    sent_groups = 0
    failed_groups = 0
    pinned_count = 0
    sent_users = 0
    failed_users = 0

    # 1. Group Broadcast
    if not skip_groups:
        served_chats = await get_served_chats()
        total_groups = len(served_chats)
        await status_msg.edit_text(f"📢 <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ {total_groups} ɢʀᴏᴜᴘs...</b>")

        for idx, chat in enumerate(served_chats, 1):
            chat_id = int(chat["chat_id"])
            try:
                if reply_msg:
                    m = await reply_msg.copy(chat_id)
                else:
                    m = await app.send_message(chat_id, text=query)

                if pin_silent:
                    try:
                        await m.pin(disable_notification=True)
                        pinned_count += 1
                    except Exception:
                        pass
                elif pin_loud:
                    try:
                        await m.pin(disable_notification=False)
                        pinned_count += 1
                    except Exception:
                        pass

                sent_groups += 1

            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                try:
                    if reply_msg:
                        await reply_msg.copy(chat_id)
                    else:
                        await app.send_message(chat_id, text=query)
                    sent_groups += 1
                except Exception:
                    failed_groups += 1
            except ChatWriteForbidden:
                await remove_served_chat(chat_id)
                failed_groups += 1
            except Exception:
                failed_groups += 1

            # Update progress every 25 groups
            if idx % 25 == 0 or idx == total_groups:
                try:
                    await status_msg.edit_text(
                        f"📢 <b>ɢʀᴏᴜᴘ ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n"
                        f"• ᴘʀᴏɢʀᴇss: `{idx}/{total_groups}`\n"
                        f"• sᴇɴᴛ: `{sent_groups}`\n"
                        f"• ғᴀɪʟᴇᴅ: `{failed_groups}`"
                    )
                except Exception:
                    pass

    # 2. Users Broadcast
    if to_users:
        served_users = await get_served_users()
        total_users = len(served_users)
        await status_msg.edit_text(f"👤 <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ {total_users} ᴜsᴇʀs...</b>")

        for idx, user in enumerate(served_users, 1):
            user_id = int(user["user_id"])
            try:
                if reply_msg:
                    await reply_msg.copy(user_id)
                else:
                    await app.send_message(user_id, text=query)
                sent_users += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                try:
                    if reply_msg:
                        await reply_msg.copy(user_id)
                    else:
                        await app.send_message(user_id, text=query)
                    sent_users += 1
                except Exception:
                    failed_users += 1
            except (UserIsBlocked, InputUserDeactivated):
                failed_users += 1
            except Exception:
                failed_users += 1

            if idx % 25 == 0 or idx == total_users:
                try:
                    await status_msg.edit_text(
                        f"👤 <b>ᴜsᴇʀ ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss...</b>\n\n"
                        f"• ᴘʀᴏɢʀᴇss: `{idx}/{total_users}`\n"
                        f"• sᴇɴᴛ: `{sent_users}`\n"
                        f"• ғᴀɪʟᴇᴅ: `{failed_users}`"
                    )
                except Exception:
                    pass

    IS_BROADCASTING = False

    result_text = (
        "✅ **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!**\n\n"
        f"👥 **ɢʀᴏᴜᴘs sᴇɴᴛ:** `{sent_groups}`\n"
        f"❌ **ɢʀᴏᴜᴘs ғᴀɪʟᴇᴅ:** `{failed_groups}`\n"
        f"📌 **ᴘɪɴɴᴇᴅ:** `{pinned_count}`\n"
    )
    if to_users:
        result_text += (
            f"👤 **ᴜsᴇʀs sᴇɴᴛ:** `{sent_users}`\n"
            f"❌ **ᴜsᴇʀs ғᴀɪʟᴇᴅ:** `{failed_users}`\n"
        )

    try:
        await status_msg.edit_text(result_text)
    except Exception:
        await message.reply_text(result_text)
