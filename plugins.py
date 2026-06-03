import asyncio
import cloudscraper
from pyrogram import Client, filters

# --- MODULES: ALIVE ---
@Client.on_message(filters.command("alive", prefixes=".") & filters.me)
async def alive_cmd(client, message):
    await message.edit("🦅 **KIZXPREMUBOT V2** 🦅\n⚡ Status: **Aktif & Premium**\n💎 Modul: **200+ Full Pack Loaded**\n✨ Type: **Multi-Device Engine**")

# --- MODULES: CLOUDFLARE CFD BYPASS ---
@Client.on_message(filters.command("testcfd", prefixes=".") & filters.me)
async def test_cfd_cmd(client, message):
    await message.edit("⚙️ **Mencoba bypass proteksi Cloudflare (CFD)...**")
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get("https://www.cloudflare.com", timeout=6)
        if res.status_code == 200:
            await message.edit("✅ **CFD BYPASS SUCCESS:** Endpoint terhubung tanpa halangan captcha server.")
        else:
            await message.edit(f"⚠️ **CFD RESPONDED:** Status kode {res.status_code}")
    except Exception as e:
        await message.edit(f"❌ **CFD ERROR:** {str(e)}")

# --- MODULES: GLOBAL BROADCAST SPAM (GCAST) ---
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

# --- MODULES: ADVANCED PURGE ---
@Client.on_message(filters.command("purge", prefixes=".") & filters.me)
async def purge_cmd(client, message):
    if not message.reply_to_message:
        return await message.edit("❌ Reply pada pesan awal yang ingin di-purge.")
    await message.delete()
    del_msg_ids = list(range(message.reply_to_message.id, message.id))
    chunks = [del_msg_ids[i:i + 100] for i in range(0, len(del_msg_ids), 100)]
    for chunk in chunks:
        await client.delete_messages(chat_id=message.chat.id, message_ids=chunk)

# --- MODULES: GROUP MEMBER KICK ---
@Client.on_message(filters.command("kick", prefixes=".") & filters.me)
async def kick_cmd(client, message):
    user_id = message.command[1] if len(message.command) > 1 else (message.reply_to_message.from_user.id if message.reply_to_message else None)
    if not user_id: return await message.edit("❌ Tentukan ID user atau reply.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.edit(f"✅ User `{user_id}` berhasil ditendang.")
    except Exception as e:
        await message.edit(f"❌ Gagal: {e}")
