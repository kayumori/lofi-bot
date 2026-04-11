import discord
import aiohttp
import os
import traceback
from aiohttp import web
import asyncio

print("start", flush=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TARGET_CHANNEL_ID = 1406875565440368706
LOFI_APP_ID = "1230610135274225734"
API_BASE = "https://discord.com/api/v10"

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
bot = discord.Client(intents=intents)

activity_running = False


@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}", flush=True)


@bot.event
async def on_voice_state_update(member, before, after):
    global activity_running
    print(f"VC: {member}", flush=True)

    if before.channel is None and after.channel is not None:
        if after.channel.id != TARGET_CHANNEL_ID:
            return
        if activity_running:
            print("already running", flush=True)
            return

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
                        activity_running = True
                        print("Lofi started!", flush=True)
                        msg_url = API_BASE + "/channels/" + str(channel_id) + "/messages"
                        data = await resp.json() if not isinstance(text, dict) else text
                        import json
                        data = json.loads(text)
                        code = data.get("code", "")
                        link = "https://discord.gg/" + code
                        msg_payload = {"content": "作業のお供にLofi音楽はいかがですか？☕\n" + link}
                        async with session.post(msg_url, json=msg_payload, headers=headers) as msg_resp:
                            print(f"msg resp: {msg_resp.status}", flush=True)
                    else:
                        print(f"error: {resp.status} {text}", flush=True)
        except Exception as e:
            print(f"err: {e}", flush=True)
            traceback.print_exc()

    if before.channel is not None and before.channel.id == TARGET_CHANNEL_ID:
        vc = bot.get_channel(TARGET_CHANNEL_ID)
        if vc and len(vc.members) == 0:
            activity_running = False
            print("reset", flush=True)


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
    print(f"web: {port}", flush=True)
    try:
        await bot.start(BOT_TOKEN)
    except Exception as e:
        print(f"bot err: {e}", flush=True)
        traceback.print_exc()


try:
    asyncio.run(start())
except Exception as e:
    print(f"fatal: {e}", flush=True)
    traceback.print_exc()
