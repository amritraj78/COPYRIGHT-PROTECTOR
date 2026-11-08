import time
import psutil
import platform
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
)
from config import BOT_USERNAME, OWNER_ID, SUDO_USERS
from PROTECTOR import PROTECTOR as app, boot
from PROTECTOR.helper.mongo import (
    add_served_user,
    add_served_chat,
    get_total_violations,
    get_served_chats,
    get_served_users,
)

START_TEXT = """<b>🛡️ ᴄᴏᴘʏʀɪɢʜᴛ & ᴀɴᴛɪ-ʟᴇᴀᴋ ᴘʀᴏᴛᴇᴄᴛᴏʀ ᴠ2.0</b>

ʜᴇʏ {mention} 👋

ɪ ᴀᴍ <b>ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ</b>, ᴀ ʜɪɢʜ-ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ᴛᴏ sᴀғᴇɢᴜᴀʀᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ғʀᴏᴍ:

• 🚫 <b>ᴄᴏᴘʏʀɪɢʜᴛ & ᴅᴍᴄᴀ sᴛʀɪᴋᴇs</b> (ғᴏʀᴡᴀʀᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ)
• 🧲 <b>ᴘɪʀᴀᴄʏ & ᴛᴏʀʀᴇɴᴛ ғɪʟᴇs</b> (ᴍᴀɢɴᴇᴛ, .ᴛᴏʀʀᴇɴᴛ, ʟᴇᴀᴋs)
• 🔗 <b>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ʟɪɴᴋs & ɪɴᴠɪᴛᴇs</b>
• 📝 <b>ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ʙʏᴘᴀss ᴀʙᴜsᴇ</b>
• 📢 <b>ᴀɴᴏɴʏᴍᴏᴜs ᴄʜᴀɴɴᴇʟ ɪᴍᴘᴇʀsᴏɴᴀᴛᴏʀs</b>

ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ɢʀᴀɴᴛ **ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs** ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ!
"""

HELP_TEXT = """<b>📖 ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ - ʜᴇʟᴘ ᴍᴇɴᴜ</b>

sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴇᴀᴛᴜʀᴇs:
"""

HELP_PROTECTION_TEXT = """<b>🛡️ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ғᴇᴀᴛᴜʀᴇs</b>

• <b>ᴀɴᴛɪ-ғᴏʀᴡᴀʀᴅ</b>:
  ᴅᴇʟᴇᴛᴇs ᴍᴇssᴀɢᴇs ғᴏʀᴡᴀʀᴅᴇᴅ ғʀᴏᴍ ᴄʜᴀɴɴᴇʟs ᴏʀ ᴜsᴇʀs ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ᴅᴍᴄᴀ ᴄᴏᴘʏʀɪɢʜᴛ ᴛᴀᴋᴇᴅᴏᴡɴs.

• <b>ᴀɴᴛɪ-ᴘɪʀᴀᴄʏ & ᴛᴏʀʀᴇɴᴛ</b>:
  ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇᴛᴇᴄᴛs ᴀɴᴅ ʀᴇᴍᴏᴠᴇs `.ᴛᴏʀʀᴇɴᴛ`, ᴍᴀɢɴᴇᴛ ʟɪɴᴋs, ᴄᴀᴍʀɪᴘ, ʟᴇᴀᴋᴇᴅ ᴄᴏᴜʀsᴇs, ᴀɴᴅ ᴘɪʀᴀᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ.

• <b>ᴀɴᴛɪ-ʟɪɴᴋ & ɪɴᴠɪᴛᴇ</b>:
  ʙʟᴏᴄᴋs ᴛᴇʟᴇɢʀᴀᴍ ɪɴᴠɪᴛᴇ ʟɪɴᴋs (`t.me/+`, `t.me/joinchat`) ᴀɴᴅ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ sᴘᴀᴍ URLs.

• <b>ᴀɴᴛɪ-ᴇᴅɪᴛ ᴇxᴘʟᴏɪᴛ</b>:
  ᴍᴏɴɪᴛᴏʀs ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇs. ɪғ ᴀ ᴜsᴇʀ ᴇᴅɪᴛs ᴀ ɴᴏʀᴍᴀʟ ᴍᴇssᴀɢᴇ ɪɴᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ᴍᴀᴛᴇʀɪᴀʟ, ɪᴛ ɪs ɪɴsᴛᴀɴᴛʟʏ ᴅᴇʟᴇᴛᴇᴅ.

• <b>ᴀɴᴛɪ-ᴄʜᴀɴɴᴇʟ</b>:
  ʙʟᴏᴄᴋs ᴍᴇssᴀɢᴇs sᴇɴᴛ ᴏɴ ʙᴇʜᴀʟғ ᴏғ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟs.
"""

HELP_ADMIN_TEXT = """<b>⚙️ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>

• `/settings` - ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴs
• `/protect on` - ᴇɴᴀʙʟᴇ ᴀʟʟ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ sʜɪᴇʟᴅs ɪɴsᴛᴀɴᴛʟʏ
• `/protect off` - ᴅɪsᴀʙʟᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ sʜɪᴇʟᴅs
• `/whitelist [reply/user_id]` - ᴡʜɪᴛᴇʟɪsᴛ ᴀ ᴜsᴇʀ (ᴇxᴇᴍᴘᴛ ғʀᴏᴍ ғɪʟᴛᴇʀs)
• `/unwhitelist [reply/user_id]` - ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ
• `/whitelisted` - ᴠɪᴇᴡ ᴀʟʟ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴜsᴇʀs ɪɴ ᴄʜᴀᴛ
• `/purge [reply]` - ᴘᴜʀɢᴇ/ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ᴜᴘ ᴛᴏ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ
"""

HELP_SUDO_TEXT = """<b>👑 sᴜᴅᴏ & ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅs</b>

• `/stats` - ɢʟᴏʙᴀʟ sʏsᴛᴇᴍ & ᴘʀᴏᴛᴇᴄᴛɪᴏɴ sᴛᴀᴛɪsᴛɪᴄs
• `/broadcast` - ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ sᴇʀᴠᴇᴅ ɢʀᴏᴜᴘs
• `/broadcast -user` - ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴀʟʟ ʙᴏᴛ ᴜsᴇʀs
• `/broadcast -pin` - ʙʀᴏᴀᴅᴄᴀsᴛ ᴀɴᴅ ᴘɪɴ sɪʟᴇɴᴛʟʏ
• `/auth <user_id>` - ɢʀᴀɴᴛ ɢʟᴏʙᴀʟ sᴜᴅᴏ ᴘʀɪᴠɪʟᴇɢᴇs
• `/unauth <user_id>` - ʀᴇᴠᴏᴋᴇ sᴜᴅᴏ ᴘʀɪᴠɪʟᴇɢᴇs
• `/listauth` - ʟɪsᴛ ᴀʟʟ ɢʟᴏʙᴀʟ sᴜᴅᴏ ᴜsᴇʀs
"""


def format_uptime(seconds: float) -> str:
    secs = int(seconds)
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    minutes, secs = divmod(secs, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def format_bytes(byte_count: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if byte_count < 1024.0:
            return f"{byte_count:.2f} {unit}"
        byte_count /= 1024.0
    return f"{byte_count:.2f} PB"


def get_start_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        ],
        [
            InlineKeyboardButton("📖 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_menu"),
            InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats_btn"),
        ],
        [
            InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url="https://t.me/Villanns"),
            InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url="https://t.me/amrit_feel"),
        ],
    ])


@app.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    user = message.from_user
    if user:
        await add_served_user(user.id)
    if message.chat and message.chat.type.name in ["GROUP", "SUPERGROUP"]:
        await add_served_chat(message.chat.id)
        await message.reply_text(
            f"🛡️ <b>ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ɪs ᴀᴄᴛɪᴠᴇ!</b>\n\n"
            f"ᴛʜɪs ɢʀᴏᴜᴘ ɪs ɴᴏᴡ ᴘʀᴏᴛᴇᴄᴛᴇᴅ. ᴜsᴇ `/settings` ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ sʜɪᴇʟᴅs.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ ᴄᴏɴғɪɢᴜʀᴇ sᴇᴛᴛɪɴɢs", callback_data="open_group_settings")]
            ])
        )
        return

    mention = user.mention if user else "Friend"
    await message.reply_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=get_start_markup(),
        disable_web_page_preview=True
    )


@app.on_message(filters.command("ping"))
async def ping_handler(_, message: Message):
    start = time.time()
    msg = await message.reply_text("⚡ <i>ᴘɪɴɢɪɴɢ...</i>")
    delta_ping = round((time.time() - start) * 1000, 2)
    uptime = format_uptime(time.time() - boot)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()

    reply_text = (
        f"🏓 **ᴘᴏɴɢ!** `{delta_ping} ᴍs`\n\n"
        f"⏱️ **ᴜᴘᴛɪᴍᴇ:** `{uptime}`\n"
        f"🖥️ **ᴄᴘᴜ:** `{cpu}%`\n"
        f"💾 **ʀᴀᴍ:** `{format_bytes(mem.used)} / {format_bytes(mem.total)}`\n"
        f"🐍 **ᴘʏᴛʜᴏɴ:** `v{platform.python_version()}`\n"
        f"🛡️ **sᴛᴀᴛᴜs:** `sᴇᴄᴜʀᴇ & ᴏɴʟɪɴᴇ`"
    )
    await msg.edit_text(
        reply_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="refresh_ping")]
        ])
    )


@app.on_message(filters.command("help"))
async def help_handler(_, message: Message):
    user = message.from_user
    if user:
        await add_served_user(user.id)
    buttons = [
        [
            InlineKeyboardButton("🛡️ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ", callback_data="help_protection"),
            InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ", callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("👑 sᴜᴅᴏ & ᴏᴡɴᴇʀ", callback_data="help_sudo"),
        ],
        [
            InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ •", callback_data="back_to_start"),
        ]
    ]
    await message.reply_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )


# --- Callback Query Navigation Handlers ---

@app.on_callback_query(filters.regex("^help_menu$"))
async def help_menu_cb(_, query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton("🛡️ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ", callback_data="help_protection"),
            InlineKeyboardButton("⚙️ ᴀᴅᴍɪɴ", callback_data="help_admin"),
        ],
        [
            InlineKeyboardButton("👑 sᴜᴅᴏ & ᴏᴡɴᴇʀ", callback_data="help_sudo"),
        ],
        [
            InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ •", callback_data="back_to_start"),
        ]
    ]
    await query.message.edit_text(HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^help_protection$"))
async def help_protection_cb(_, query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ •", callback_data="help_menu")]
    ]
    await query.message.edit_text(HELP_PROTECTION_TEXT, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^help_admin$"))
async def help_admin_cb(_, query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ •", callback_data="help_menu")]
    ]
    await query.message.edit_text(HELP_ADMIN_TEXT, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^help_sudo$"))
async def help_sudo_cb(_, query: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("• ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ •", callback_data="help_menu")]
    ]
    await query.message.edit_text(HELP_SUDO_TEXT, reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_cb(_, query: CallbackQuery):
    user = query.from_user
    mention = user.mention if user else "Friend"
    await query.message.edit_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=get_start_markup(),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex("^vip_back$"))
async def vip_back_cb(_, query: CallbackQuery):
    user = query.from_user
    mention = user.mention if user else "Friend"
    await query.message.edit_text(
        text=START_TEXT.format(mention=mention),
        reply_markup=get_start_markup(),
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex("^refresh_ping$"))
async def refresh_ping_cb(_, query: CallbackQuery):
    start = time.time()
    uptime = format_uptime(time.time() - boot)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    delta_ping = round((time.time() - start) * 1000, 2)

    reply_text = (
        f"🏓 **ᴘᴏɴɢ!** `{delta_ping} ᴍs`\n\n"
        f"⏱️ **ᴜᴘᴛɪᴍᴇ:** `{uptime}`\n"
        f"🖥️ **ᴄᴘᴜ:** `{cpu}%`\n"
        f"💾 **ʀᴀᴍ:** `{format_bytes(mem.used)} / {format_bytes(mem.total)}`\n"
        f"🐍 **ᴘʏᴛʜᴏɴ:** `v{platform.python_version()}`\n"
        f"🛡️ **sᴛᴀᴛᴜs:** `sᴇᴄᴜʀᴇ & ᴏɴʟɪɴᴇ`"
    )
    try:
        await query.message.edit_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="refresh_ping")]
            ])
        )
    except Exception:
        await query.answer("Already updated!", show_alert=False)


@app.on_callback_query(filters.regex("^stats_btn$"))
async def stats_btn_cb(_, query: CallbackQuery):
    uptime = format_uptime(time.time() - boot)
    total_chats = len(await get_served_chats())
    total_users = len(await get_served_users())
    total_violations = await get_total_violations()

    text = (
        f"📊 **ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ sᴛᴀᴛs**\n\n"
        f"👥 **sᴇʀᴠᴇᴅ ᴜsᴇʀs:** `{total_users}`\n"
        f"🛡️ **ᴘʀᴏᴛᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs:** `{total_chats}`\n"
        f"🚫 **ᴠɪᴏʟᴀᴛɪᴏɴs sᴛᴏᴘᴘᴇᴅ:** `{total_violations}`\n"
        f"⏱️ **ᴜᴘᴛɪᴍᴇ:** `{uptime}`\n"
    )
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="back_to_start")]
        ])
    )


@app.on_callback_query(filters.regex("^close_menu$"))
async def close_menu_cb(_, query: CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        await query.answer("Closed!")
