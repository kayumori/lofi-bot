import discord
import aiohttp
import os
import traceback
from aiohttp import web
import asyncio
import json
import random

print("start", flush=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TARGET_CHANNEL_ID = 1406875565440368706
LOFI_APP_ID = "1230610135274225734"
API_BASE = "https://discord.com/api/v10"

GREETINGS = [
    "\u672c\u65e5\u3082\u304a\u75b2\u308c\u69d8\u3067\u3059\u263a\ufe0f",
    "\u4eca\u65e5\u3082\u3044\u3044\u4f5c\u696d\u65e5\u548c\u3067\u3059\u306d\u2600\ufe0f",
    "\u3086\u3063\u304f\u308a\u3057\u3066\u3044\u3063\u3066\u304f\u3060\u3055\u3044\u306d\ud83c\udf75",
    "\u96c6\u4e2d\u30e2\u30fc\u30c9\u3001\u5fdc\u63f4\u3057\u3066\u307e\u3059\u3088\ud83d\udcaa",
    "\u3044\u3089\u3063\u3057\u3083\u3044\u307e\u305b\u3001\u3054\u3086\u3063\u304f\u308a\u3069\u3046\u305e\ud83c\udf07",
    "\u4eca\u65e5\u3082\u4e00\u7dd2\u306b\u9811\u5f35\u308a\u307e\u3057\u3087\u3046\u2728",
    "\u304a\u5f85\u3061\u3057\u3066\u304a\u308a\u307e\u3057\u305f\u263a\ufe0f",
    "\u304a\u5e30\u308a\u306a\u3055\u3044\u3001\u304a\u5f85\u3061\u3057\u3066\u304a\u308a\u307e\u3057\u305f\ud83c\udf07",
    "\u4eca\u65e5\u306e\u8abf\u5b50\u306f\u3044\u304b\u304c\u3067\u3059\u304b\uff1f\ud83d\ude0a",
    "\u30ea\u30e9\u30c3\u30af\u30b9\u3057\u3066\u53d6\u308a\u7d44\u3093\u3067\u3044\u304d\u307e\u3057\u3087\u3046\ud83d\udeb6",
    "\u304a\u4ed5\u4e8b\u304a\u75b2\u308c\u69d8\u3067\u3059\u3001\u3069\u3046\u305e\u3054\u81ea\u7531\u306b\ud83c\udf07",
    "\u3044\u3064\u3082\u3042\u308a\u304c\u3068\u3046\u3054\u3056\u3044\u307e\u3059\u3001\u4eca\u65e5\u3082\u3069\u3046\u305e\u263a\ufe0f",
    "\u81ea\u5206\u306e\u30da\u30fc\u30b9\u3067\u3001\u7121\u7406\u305b\u305a\u3044\u304d\u307e\u3057\u3087\u3046\ud83c\udf31",
    "\u3055\u3042\u3001\u4f5c\u696d\u306e\u6642\u9593\u3067\u3059\u3088\u2728",
    "\u4eca\u65e5\u306e\u904b\u52e2\u306f\u5927\u5409\u3067\u3059\uff01\u306a\u3093\u3061\u3083\u3063\u3066\ud83d\ude0c",
]

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
bot = discord.Client(intents=intents)

activity_running = False
invite_lock = asyncio.Lock()


@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}", flush=True)


@bot.event
async def on_resumed():
    print("Bot reconnected!", flush=True)


@bot.event
async def on_disconnect():
    print("Bot disconnected...", flush=True)


@bot.event
async def on_voice_state_update(member, before, after):
    global activity_running

    if before.channel is None and after.channel is not None:
        if after.channel.id != TARGET_CHANNEL_ID:
            return

        async with invite_lock:
            if activity_running:
                return
            activity_running = True

            channel_id = after.channel.id
            invite_url = API_BASE + "/channels/" + str(channel_id) + "/invites"
            headers = {"Authorization": "Bot " + BOT_TOKEN, "Content-Type": "application/json"}
            payload = {"max_age": 86400, "target_type": 2, "target_application_id": LOFI_APP_ID}

            print("creating invite...", flush=True)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(invite_url, json=payload, headers=headers) as resp:
                        text = await resp.text()
                        print(f"invite resp: {resp.status}", flush=True)
                        if resp.status == 200:
                            data = json.loads(text)
                            code = data.get("code", "")
                            link = "https://discord.gg/" + code
                            msg_url = API_BASE + "/channels/" + str(channel_id) + "/messages"
                            greeting = random.choice(GREETINGS)
                            msg_payload = {"content": greeting + "\n" + link + "\n\u4f5c\u696d\u306e\u304a\u4f9b\u306bLofi\u97f3\u697d\u306f\u3044\u304b\u304c\u3067\u3059\u304b\uff1f\u2615"}
                            async with session.post(msg_url, json=msg_payload, headers=headers) as msg_resp:
                                print(f"msg resp: {msg_resp.status}", flush=True)
                        else:
                            activity_running = False
                            print(f"error: {resp.status} {text}", flush=True)
            except Exception as e:
                activity_running = False
                print(f"err: {e}", flush=True)
                traceback.print_exc()

    if before.channel is not None and before.channel.id == TARGET_CHANNEL_ID:
        vc = bot.get_channel(TARGET_CHANNEL_ID)
        if vc and len(vc.members) == 0:
            activity_running = False
            print("reset", flush=True)


async def health(request):
    return web.Response(text="OK")


async def run_bot():
    while True:
        try:
            print("Bot starting...", flush=True)
            await bot.start(BOT_TOKEN)
        except Exception as e:
            print(f"Bot crashed: {e}, restarting in 10s...", flush=True)
            traceback.print_exc()
            await asyncio.sleep(10)


async def start():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"web: {port}", flush=True)
    await run_bot()


try:
    asyncio.run(start())
except Exception as e:
    print(f"fatal: {e}", flush=True)
    traceback.print_exc()
