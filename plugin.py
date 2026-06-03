import os
import asyncio
import importlib
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===================== CONFIG UTAMA (SIAP DIEDIT) =====================
BOT_TOKEN = "8796670391:AAESeHo9zhwB6RU4ebqik-MBZTjgNLvyU-4"
OWNER_ID = 1983044179

# API ID & API HASH Resmi Telegram Android (100% Aman & Anti-Hack)
API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
# ======================================================================

bot = Client("KizxPremUbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
running_ubots = {}

def load_plugins_into_ubot(ubot_client):
    if os.path.exists("./plugins"):
        for filename in os.listdir("./plugins"):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"plugins.{filename[:-3]}"
                if module_name in os.sys.modules:
                    module = importlib.reload(os.sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, "handlers"):
                        for handler, group in attr.handlers:
                            ubot_client.add_handler(handler, group)

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    text = (
        f"👋 HALO **{message.from_user.first_name}** !\n\n"
        "⚡ 💎 **KizxPremUbot** ADALAH BOT YANG DAPAT MEMBUAT USERBOT DENGAN MUDAH\n\n"
        "🚀 BOT INI DIKEMBANGKAN OLEH OWNER\n\n"
        "**CARA SEWA USERBOT (200 MODULES FULL):**\n"
        "Sila buat pembayaran manual menggunakan QR Code KIZX STORE. "
        "Selepas bayar, hantar bukti resit kepada Owner untuk Kelulusan (Approval).\n\n"
        "Sila tekan butang di bawah untuk memproses."
    )
    buttons = [
        [InlineKeyboardButton("💳 BAYAR SEWA (QR PAYMENT) 💳", callback_data="bayar_qr")],
        [InlineKeyboardButton("🦅 BUAT USERBOT (SELEPAS APPROVE) 🦅", callback_data="buat_ubot")],
        [InlineKeyboardButton("🦅 SUPPORT OWNER 🦅", url="https://t.me/Kizxx")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex("bayar_qr"))
async def bayar_qr_handler(client, callback_query):
    text_pay = (
        "📸 **KIZX STORE MANUAL QR PAYMENT**\n\n"
        "1. Sila scan QR Code di atas dan selesaikan bayaran sewa.\n"
        "2. Selepas berjaya, hantar gambar **Resit Pembayaran (Slip)** di sini.\n\n"
        "⏳ Sila hantar gambar resit anda sekarang..."
    )
    await callback_query.message.reply_photo(
        photo="https://files.catbox.moe/s1sadp.jpg", 
        caption=text_pay
    )

if __name__ == "__main__":
    print("🦅 KIZXPREMUBOT ONLINE!")
    bot.run()