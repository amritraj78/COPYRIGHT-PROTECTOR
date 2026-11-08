import asyncio
import importlib
import logging
import time
from aiohttp import web
from pyrogram import idle
import PROTECTOR as protector_mod
from PROTECTOR import PROTECTOR, boot
from PROTECTOR.modules import ALL_MODULES
from config import LOGGER_ID, OWNER_ID, PORT

logger = logging.getLogger("PROTECTOR.main")


async def health_check_handler(request):
    uptime_sec = int(time.time() - boot)
    return web.json_response({
        "status": "healthy",
        "bot": protector_mod.BOT_USERNAME,
        "uptime_seconds": uptime_sec,
        "modules_loaded": len(ALL_MODULES)
    })

async def root_handler(request):
    return web.json_response({
        "status": "ok",
        "service": "Copyright Protector Bot",
        "bot": f"@{protector_mod.BOT_USERNAME}",
        "version": "2.0.0"
    })

async def start_web_server():
    try:
        app = web.Application()
        app.router.add_get("/", root_handler)
        app.router.add_get("/health", health_check_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Health check web server running on port {PORT}")
        return runner
    except Exception as e:
        logger.warning(f"Could not start web server on port {PORT}: {e}")
        return None


async def main():
    logger.info("Starting Copyright Protector Bot...")
    
    # Start Pyrogram Client
    await PROTECTOR.start()
    me = await PROTECTOR.get_me()
    protector_mod.BOT_ID = me.id
    protector_mod.BOT_USERNAME = me.username
    protector_mod.BOT_NAME = f"{me.first_name} {me.last_name or ''}".strip()
    
    logger.info(f"Bot connected: @{me.username} ({me.id})")

    # Start HTTP health check server for Koyeb/Render
    web_runner = await start_web_server()

    # Start background keep-alive ping loop to prevent Koyeb idle sleep
    async def keep_alive_self_ping():
        ping_url = "https://copyright-protector-villianking-f3011d6a.apps.mistral.run/health"
        logger.info(f"Keep-alive self-pinger started for {ping_url}")
        await asyncio.sleep(60)
        while True:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(ping_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        logger.info(f"Keep-alive self-ping sent ({resp.status})")
            except Exception as e:
                logger.debug(f"Keep-alive ping error: {e}")
            await asyncio.sleep(300)

    asyncio.create_task(keep_alive_self_ping())

    # Load all modules dynamically
    loaded = 0
    for mod_name in ALL_MODULES:
        try:
            importlib.import_module(f"PROTECTOR.modules.{mod_name}")
            loaded += 1
        except Exception as e:
            logger.error(f"Failed to load module {mod_name}: {e}")

    logger.info(f"Successfully loaded {loaded}/{len(ALL_MODULES)} modules.")

    # Send startup message to Logger Chat or Owner
    startup_msg = (
        "🛡️ **ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʙᴏᴛ ɪs ᴏɴʟɪɴᴇ!** ✅\n\n"
        f"🤖 **ʙᴏᴛ:** @{protector_mod.BOT_USERNAME}\n"
        f"🆔 **ɪᴅ:** `{protector_mod.BOT_ID}`\n"
        f"📦 **ᴍᴏᴅᴜʟᴇs:** `{loaded}` ʟᴏᴀᴅᴇᴅ\n"
        f"🌐 **ᴡᴇʙ ᴘᴏʀᴛ:** `{PORT}`\n"
        f"⚡ **ᴠᴇʀsɪᴏɴ:** `v2.0.0 Premium`\n\n"
        "✨ _All protection filters, auto-moderation, and database systems are active._"
    )

    sent = False
    if LOGGER_ID:
        try:
            await PROTECTOR.send_message(LOGGER_ID, startup_msg)
            sent = True
        except Exception as e:
            logger.warning(f"Could not send log to LOGGER_ID ({LOGGER_ID}): {e}")

    if not sent and OWNER_ID:
        try:
            await PROTECTOR.send_message(OWNER_ID, startup_msg)
        except Exception:
            pass

    print(f"\n==========================================")
    print(f" Copyright Protector Bot Started!")
    print(f" Username: @{protector_mod.BOT_USERNAME}")
    print(f" Web Port: {PORT}")
    print(f" Status  : ONLINE & PROTECTING")
    print(f"==========================================\n")

    # Idle until termination
    await idle()

    # Cleanup on exit
    logger.info("Stopping bot and services...")
    if web_runner:
        await web_runner.cleanup()
    await PROTECTOR.stop()
    logger.info("Bot stopped successfully.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
