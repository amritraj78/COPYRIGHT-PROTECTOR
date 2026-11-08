from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
)
from config import OWNER_ID, SUDO_USERS
from PROTECTOR import PROTECTOR as app
from PROTECTOR.helper.mongo import (
    get_chat_settings,
    set_chat_setting,
    toggle_chat_setting,
    get_auth_users,
)
from PROTECTOR.modules.protection import is_admin


def get_status_badge(is_active: bool) -> str:
    return "✅ ᴏɴ" if is_active else "❌ ᴏғғ"


def build_settings_keyboard(settings: dict, chat_id: int) -> InlineKeyboardMarkup:
    protect_mode = settings.get("protect_mode", True)
    anti_fwd = settings.get("anti_forward", True)
    anti_piracy = settings.get("anti_piracy", True)
    anti_links = settings.get("anti_links", True)
    anti_edit = settings.get("anti_edited", True)
    anti_chnl = settings.get("anti_channel", False)
    delete_alert = settings.get("delete_alert", True)

    master_badge = "🛡️ ᴘʀᴏᴛᴇᴄᴛ: ᴀᴄᴛɪᴠᴇ ✅" if protect_mode else "🛡️ ᴘʀᴏᴛᴇᴄᴛ: ᴘᴀᴜsᴇᴅ ⏸️"

    buttons = [
        [
            InlineKeyboardButton(master_badge, callback_data=f"toggle_set:protect_mode:{chat_id}")
        ],
        [
            InlineKeyboardButton(f"ғᴏʀᴡᴀʀᴅ sʜɪᴇʟᴅ: {get_status_badge(anti_fwd)}", callback_data=f"toggle_set:anti_forward:{chat_id}"),
            InlineKeyboardButton(f"ᴘɪʀᴀᴄʏ / ᴛᴏʀʀᴇɴᴛ: {get_status_badge(anti_piracy)}", callback_data=f"toggle_set:anti_piracy:{chat_id}"),
        ],
        [
            InlineKeyboardButton(f"ʟɪɴᴋ sʜɪᴇʟᴅ: {get_status_badge(anti_links)}", callback_data=f"toggle_set:anti_links:{chat_id}"),
            InlineKeyboardButton(f"ᴇᴅɪᴛ sʜɪᴇʟᴅ: {get_status_badge(anti_edit)}", callback_data=f"toggle_set:anti_edited:{chat_id}"),
        ],
        [
            InlineKeyboardButton(f"ᴄʜᴀɴɴᴇʟ sᴘᴀᴍ: {get_status_badge(anti_chnl)}", callback_data=f"toggle_set:anti_channel:{chat_id}"),
            InlineKeyboardButton(f"ᴀʟᴇʀᴛs: {get_status_badge(delete_alert)}", callback_data=f"toggle_set:delete_alert:{chat_id}"),
        ],
        [
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ ᴍᴇɴᴜ", callback_data="close_menu")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


SETTINGS_PANEL_TEXT = """<b>⚙️ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ sᴇᴛᴛɪɴɢs</b>

<b>ᴄʜᴀᴛ:</b> <code>{title}</code>
<b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_id}</code>

<i>ᴄʟɪᴄᴋ ᴏɴ ᴀɴʏ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ sʜɪᴇʟᴅs:</i>
"""


@app.on_message(filters.command("settings") & filters.group)
async def settings_command_handler(_, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    # Check if user is admin or sudo
    if not await is_admin(chat.id, user.id):
        auth_users = await get_auth_users()
        if user.id != OWNER_ID and user.id not in SUDO_USERS and user.id not in auth_users:
            return await message.reply_text("❌ <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴛᴏ ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs!</b>")

    settings = await get_chat_settings(chat.id)
    await message.reply_text(
        SETTINGS_PANEL_TEXT.format(title=chat.title, chat_id=chat.id),
        reply_markup=build_settings_keyboard(settings, chat.id)
    )


@app.on_message(filters.command("protect") & filters.group)
async def protect_command_handler(_, message: Message):
    chat = message.chat
    user = message.from_user
    if not user:
        return

    if not await is_admin(chat.id, user.id):
        return await message.reply_text("❌ <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ!</b>")

    if len(message.command) < 2:
        settings = await get_chat_settings(chat.id)
        current = "ENABLED ✅" if settings.get("protect_mode", True) else "DISABLED ❌"
        return await message.reply_text(
            f"ℹ️ <b>ᴄᴜʀʀᴇɴᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ sᴛᴀᴛᴜs:</b> {current}\n\n"
            f"ᴜsᴀɢᴇ: `/protect on` ᴏʀ `/protect off`"
        )

    action = message.command[1].lower()
    if action in ["on", "enable", "yes"]:
        await set_chat_setting(chat.id, "protect_mode", True)
        await message.reply_text("🛡️ <b>ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ɪs ɴᴏᴡ ғᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ!</b> ✅")
    elif action in ["off", "disable", "no"]:
        await set_chat_setting(chat.id, "protect_mode", False)
        await message.reply_text("⚠️ <b>ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ!</b> ⏸️")
    else:
        await message.reply_text("Usage: `/protect on` or `/protect off`")


@app.on_callback_query(filters.regex(r"^toggle_set:([a-z_]+):(-?\d+)$"))
async def toggle_setting_callback(_, query: CallbackQuery):
    key, chat_id_str = query.matches[0].groups()
    chat_id = int(chat_id_str)
    user = query.from_user

    if not user:
        return await query.answer("User error.", show_alert=True)

    # Permission check
    if not await is_admin(chat_id, user.id):
        auth_users = await get_auth_users()
        if user.id != OWNER_ID and user.id not in SUDO_USERS and user.id not in auth_users:
            return await query.answer("❌ You must be an admin to change settings!", show_alert=True)

    # Toggle setting in database
    new_status = await toggle_chat_setting(chat_id, key)
    updated_settings = await get_chat_settings(chat_id)

    status_str = "ENABLED ✅" if new_status else "DISABLED ❌"
    await query.answer(f"{key.replace('_', ' ').title()}: {status_str}")

    try:
        await query.message.edit_reply_markup(
            reply_markup=build_settings_keyboard(updated_settings, chat_id)
        )
    except Exception:
        pass


@app.on_callback_query(filters.regex("^open_group_settings$"))
async def open_group_settings_cb(_, query: CallbackQuery):
    chat = query.message.chat
    user = query.from_user
    if not chat or not user:
        return

    if not await is_admin(chat.id, user.id):
        return await query.answer("❌ Only admins can open settings!", show_alert=True)

    settings = await get_chat_settings(chat.id)
    await query.message.edit_text(
        SETTINGS_PANEL_TEXT.format(title=chat.title, chat_id=chat.id),
        reply_markup=build_settings_keyboard(settings, chat.id)
    )
