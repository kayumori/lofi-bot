import discord
import aiohttp
import os
import traceback
from aiohttp import web
import asyncio

print("スクリプト開始", flush=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TARGET_CHANNEL_ID = 1406875565440368706
LOFI_APP_ID = "1230610135274225734"

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
bot = discord.Client(intents=intents)

activity_running = False


@bot.event
async def on_ready():
    print(f"Bot起動したよ: {bot.user}", flush=True)


@bot.event
async def on_voice_state_update(member, before, after):
    global activity_running
    print(f"VC変化検知: {member}", flush=True)

    if before.channel is None and after.channel is not None:
        if after.channel.id != TARGET_CHANNEL_ID:
            return
        if activity_running:
            print("Activity はすでに起動中、スキップ", flush=True)
            return

        channel_id = after.channel.id
        url = f"{{https://discord.com/api/v10/channels/{channel_id}}}/invites"
        headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}
        payload = {"max_age": 86400, "target_type": 2, "target_application_id": LOFI_APP_ID}

        print("Activity招待作成中...", flush=True)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        invite_code = data.get("code", "")
                        invite_url = f"{{https://discord.gg/{invite_code}}}"
                        print(f"Invite作成成功: {invite_url}", flush=True)
                        activity_running = True

                        # VCのテキストチャットに招待リンクを送信
                        vc_channel = bot.get_channel(TARGET_CHANNEL_ID)
                        if vc_channel:
                            msg_url = f"{{https://discord.com/api/v10/channels/{channel_id}}}/messages"
                            msg_payload = {"content": f"🎶 **Lofi BGM** を起動するよ！\n▶️ ここをクリックして参加: {invite_url}"}
                            async with session.post(msg_url, json=msg_payload, headers=headers) as msg_resp:
                                print(f"メッセージ送信: {msg_resp.status}", flush=True)
                    else:
                        text = await resp.text()
                        print(f"エラー: {resp.status} - {text}", flush=True)
        except Exception as e:
            print(f"APIエラー: {e}", flush=True)
            traceback.print_exc()

    if before.channel is not None and before.channel.id == TARGET_CHANNEL_ID:
        vc = bot.get_channel(TARGET_CHANNEL_ID)
        if vc and len(vc.members) == 0:
            activity_running = False
            print("全員退出、フラグリセット", flush=True)


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
