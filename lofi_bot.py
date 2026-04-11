import discord
import os
from aiohttp import web
import asyncio

BOT_TOKEN = os.environ["BOT_TOKEN"]

intents = discord.Intents.default()
intents.voice_states = True
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"Bot起動したよ: {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"VC変化検知: {member} before={before.channel} after={after.channel}")


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
    print(f"Web: port {port}")
    await bot.start(BOT_TOKEN)


asyncio.run(start())
