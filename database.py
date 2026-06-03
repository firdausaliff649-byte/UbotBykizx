import asyncio
import cloudscraper
from pyrogram import Client, filters

# --- MODULES: ALIVE & GCAST ---
@Client.on_message(filters.command("alive", prefixes=".") & filters.me)
async def alive_cmd(client, message):
    await message.edit("🦅 **KIZXPREMUBOT V2** 🦅\n⚡ Status: **Aktif & Premium**\n💎 Modul: **200+ Full Pack Loaded**")

@Client.on_message(filters.command("gcast", prefixes=".") & filters.me)
async def gcast_cmd(client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.edit("❌ Sila masukkan teks atau reply pada media.")
    await message.edit("📢 **Mengirimkan Pesan Massal (Gcast)...**")
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    done = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, text)
                done += 1
                await asyncio.sleep(0.4)
            except:
                continue
    await message.edit(f"✅ **Gcast Berhasil:** Tersampaikan ke {done} grup.")