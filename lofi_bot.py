import discord
import os
import sys
import traceback
from aiohttp import web
import asyncio

print("スクリプト開始", flush=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
print(f"トークン長さ: {len(BOT_TOKEN)}", flush=True)
print(f"トークン先頭: {BOT_TOKEN[:5]}", flush=True)

TARGET_CHANNEL_ID = 1406875565440368706

intents = discord.Intents.default()
intents.voice_states = True
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"Bot起動したよ: {bot.user}", flush=True)


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"VC変化検知: {member}", flush=True)


async def health(request):
    return web.Response(text="OK")


async def start():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web: port {port}", flush=True)
    try:
        await bot.start(BOT_TOKEN)
    except Exception as e:
        print(f"Bot起動エラー: {e}", flush=True)
        traceback.print_exc()


try:
    asyncio.run(start())
except Exception as e:
    print(f"全体エラー: {e}", flush=True)
    traceback.print_exc()
