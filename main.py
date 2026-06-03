import os
import asyncio
import importlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from database import (
    add_ubot, remove_ubot, get_all_ubots, is_banned,
    ban_user, unban_user, add_user, get_all_users,
    create_payment, get_payment, update_payment_status
)

BOT_TOKEN = "8796670391:AAESeHo9zhwB6RU4ebqik-MBZTjgNLvyU-4"
OWNER_ID = 1983044179
API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

bot = Client("KizxPremUbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
running_ubots = {}

def load_plugins_into_ubot(ubot_client):
    try:
        module = importlib.import_module("plugins")
        importlib.reload(module)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, "handlers"):
                for handler, group in attr.handlers:
                    ubot_client.add_handler(handler, group)
    except Exception as e:
        print(f"❌ Gagal memuatkan plugins.py: {e}")

async def restart_all_ubots():
    try:
        all_saved = await get_all_ubots()
        for data in all_saved:
            u_id = data["user_id"]
            session = data["session"]
            try:
                ubot = Client(f"ubot_{u_id}", api_id=API_ID, api_hash=API_HASH, session_string=session)
                await ubot.start()
                load_plugins_into_ubot(ubot)
                running_ubots[u_id] = ubot
            except Exception as e:
                print(f"❌ Gagal: {e}")
    except Exception as e:
        print(f"❌ MongoDB: {e}")

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    if await is_banned(user_id):
        return await message.reply("⚠️ Anda telah di-blacklist.")
    await add_user(user_id)
    
    text = (
        f"👋 HALO **{message.from_user.first_name}** !\n\n"
        "⚡ 💎 **KizxPremUbot** ADALAH BOT YANG DAPAT MEMBUAT USERBOT DENGAN MUDAH\n\n"
        "Sila buat pembayaran manual menggunakan QR Code KIZX STORE untuk aktifkan."
    )
    buttons = [
        [InlineKeyboardButton("💳 BAYAR SEWA (QR PAYMENT) 💳", callback_data="bayar_qr")],
        [InlineKeyboardButton("🦅 BUAT USERBOT (SELEPAS APPROVE) 🦅", callback_data="buat_ubot")],
        [InlineKeyboardButton("🦅 SUPPORT OWNER 🦅", url="https://t.me/Kizxx")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex("bayar_qr"))
async def bayar_qr_handler(client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.message.reply_photo(
        photo="https://files.catbox.moe/s1sadp.jpg", 
        caption="⏳ Sila hantar gambar resit anda sekarang..."
    )
    
    @bot.on_message(filters.user(user_id) & filters.photo, group=3)
    async def get_receipt(cl, msg):
        await msg.reply("⏳ Resit dihantar! Menunggu kelulusan Owner...")
        await bot.send_photo(
            chat_id=OWNER_ID,
            photo=msg.photo.file_id,
            caption=f"🔔 Resit baru dari ID: `{user_id}`",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{user_id}")
            ]])
        )
        await create_payment(user_id, msg.id)
        bot.remove_handler(get_receipt, group=3)

@bot.on_callback_query(filters.regex("approve_") | filters.regex("reject_"))
async def approval_logic(client, callback_query):
    if callback_query.from_user.id != OWNER_ID: return
    action, target_user_id = callback_query.data.split("_")
    target_user_id = int(target_user_id)
    if action == "approve":
        await update_payment_status(target_user_id, "approved")
        await callback_query.message.edit_caption("✅ Approved!")
    else:
        await update_payment_status(target_user_id, "rejected")
        await callback_query.message.edit_caption("❌ Rejected!")

@bot.on_callback_query(filters.regex("buat_ubot"))
async def buat_ubot_handler(client, callback_query):
    user_id = callback_query.from_user.id
    pay_data = await get_payment(user_id)
    if not pay_data or pay_data.get("status") != "approved":
        return await callback_query.answer("⚠️ Sila bayar dahulu!", show_alert=True)
    await callback_query.message.edit_text("🔑 Sila hantar Pyrogram String Session anda:")
    
    @bot.on_message(filters.user(user_id) & filters.text, group=4)
    async def capture_session(cl, msg):
        try:
            new_ubot = Client(f"ubot_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=msg.text)
            await new_ubot.start()
            load_plugins_into_ubot(new_ubot)
            await add_ubot(user_id, msg.text)
            running_ubots[user_id] = new_ubot
            await msg.reply("✅ USERBOT PREM BERJAYA DIAKTIFKAN! Cuba `.alive`")
        except Exception as e:
            await msg.reply(f"❌ Gagal: {str(e)}")
        bot.remove_handler(capture_session, group=4)

# --- TRIK WEB SERVER TIRUAN UNTUK VERCEL ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"KizxPremUbot is running!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    server.serve_forever()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(restart_all_ubots())
    except: pass
    bot.run()

if __name__ == "__main__":
    # Jalankan bot dalam thread berasingan
    t = threading.Thread(target=run_bot)
    t.start()
    # Jalankan web server di main thread untuk Vercel
    print("🦅 KIZXPREMUBOT ONLINE!")
    run_web_server()
