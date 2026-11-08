import time
import platform
import psutil
from pyrogram import filters
from pyrogram.types import Message
from config import SUDOERS
from PROTECTOR import PROTECTOR as app, boot
from PROTECTOR.helper.mongo import (
    get_served_chats,
    get_served_users,
    get_total_violations,
)
from PROTECTOR.modules.main import format_uptime, format_bytes


@app.on_message(filters.command(["stats", "status"]))
async def stats_command_handler(_, message: Message):
    uptime = format_uptime(time.time() - boot)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    total_chats = len(await get_served_chats())
    total_users = len(await get_served_users())
    total_violations = await get_total_violations()

    stats_text = (
        "📊 **ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ - sʏsᴛᴇᴍ & ʙᴏᴛ sᴛᴀᴛs**\n\n"
        f"🛡️ **ᴘʀᴏᴛᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs:** `{total_chats}`\n"
        f"👥 **sᴇʀᴠɪᴄᴇᴅ ᴜsᴇʀs:** `{total_users}`\n"
        f"🚫 **ᴠɪᴏʟᴀᴛɪᴏɴs ʙʟᴏᴄᴋᴇᴅ:** `{total_violations}`\n\n"
        f"⏱️ **ᴜᴘᴛɪᴍᴇ:** `{uptime}`\n"
        f"🖥️ **ᴄᴘᴜ ᴜsᴀɢᴇ:** `{cpu}%`\n"
        f"💾 **ʀᴀᴍ ᴜsᴀɢᴇ:** `{format_bytes(mem.used)} / {format_bytes(mem.total)}` ({mem.percent}%)\n"
        f"📁 **ᴅɪsᴋ ᴜsᴀɢᴇ:** `{format_bytes(disk.used)} / {format_bytes(disk.total)}` ({disk.percent}%)\n\n"
        f"🐍 **ᴘʏᴛʜᴏɴ:** `v{platform.python_version()}`\n"
        f"⚡ **ᴇɴɢɪɴᴇ:** `Pyrogram v2.0.106`\n"
        f"🌐 **ᴍᴏᴅᴇ:** `Cloud Production (v2.0)`"
    )
    await message.reply_text(stats_text)
