import discord
import aiohttp
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
LOFI_APP_ID = "1051500497355956264"
TARGET_CHANNEL_ID = 1406875565440368706

intents = discord.Intents.default()
intents.voice_states = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot起動したよ〜: {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if after.channel.id != TARGET_CHANNEL_ID:
            return

        channel_id = after.channel.id
        url = f"{{https://discord.com/api/v10/channels/{channel_id}}}/activities"
        headers = {
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {"application_id": LOFI_APP_ID}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    print("Lofi Activity 起動成功🎶")
                else:
                    print(f"エラー: {resp.status} - {await resp.text()}")

bot.run(BOT_TOKEN)
