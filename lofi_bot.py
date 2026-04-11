import discord
import aiohttp
import os
from aiohttp import web
import asyncio

BOT_TOKEN = os.environ["BOT_TOKEN"]
TARGET_CHANNEL_ID = 1406875565440368706

# Lofi Records の Application ID
LOFI_APP_ID = "1051500497355956264"

intents = discord.Intents.default()
intents.voice_states = True
bot = discord.Client(intents=intents)

activity_running = False

@bot.event
async def on_ready():
    print(f"Bot起動したよ〜: {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    global activity_running

    # 誰かが対象VCに入ったとき
    if before.channel is None and after.channel is not None:
        if after.channel.id != TARGET_CHANNEL_ID:
            return

        if activity_running:
            print("Activity はすでに起動中じゃけんスキップ")
            return

        channel_id = after.channel.id

        # Embedded Activity の Invite を作成
        url = f"https://discord.com/api/v10/channels/{channel_id}/invites"
        headers = {
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "max_age": 0,
            "target_type": 2,
            "target_application_id": LOFI_APP_ID
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    invite_code = data.get("code", "")
                    print(f"Lofi Activity 起動成功🎶 Invite: {invite_code}")
                    activity_running = True

                    # VCにメッセージは送れんけど、ログで確認できる
                else:
                    text = await resp.text()
                    print(f"エラー: {resp.status} - {text}")

    # 対象VCから全員いなくなったらリセット
    if before.channel is not None and before.channel.id == TARGET_CHANNEL_ID:
        vc = bot.get_channel(TARGET_CHANNEL_ID)
        if vc and len(vc.members) == 0:
            activity_running = False
            print("全員退出 → Activity フラグリセット")

# --- ダミーWebサーバー ---
async def health(request):
    return web.Response(text="Bot is running!")

async def start():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Webサーバー起動: ポート {port}")
    await bot.start(BOT_TOKEN)

asyncio.run(start())
