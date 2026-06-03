import os
import asyncio
import importlib
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# Import fungsi pangkalan data dari database.py
from database import (
    add_ubot, remove_ubot, get_all_ubots, is_banned,
    ban_user, unban_user, add_user, get_all_users,
    create_payment, get_payment, update_payment_status
)

# ===================== CONFIG UTAMA (SIAP) =====================
BOT_TOKEN = "8796670391:AAESeHo9zhwB6RU4ebqik-MBZTjgNLvyU-4"
OWNER_ID = 1983044179

# API ID & API HASH Resmi Telegram Android
API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
# ===============================================================

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
    print("⏳ Menghidupkan kembali seluruh userbot premium...")
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
                print(f"❌ Gagal mengaktifkan userbot {u_id}: {e}")
    except Exception as e:
        print(f"❌ MongoDB bermasalah: {e}")

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    if await is_banned(user_id):
        return await message.reply("⚠️ Anda telah di-blacklist dari bot ini.")
    await add_user(user_id)
    
    text = (
        f"👋 HALO **{message.from_user.first_name}** !\n\n"
        "⚡ 💎 **KizxPremUbot** ADALAH BOT YANG DAPAT MEMBUAT USERBOT DENGAN MUDAH\n\n"
        "🚀 BOT INI DIKEMBANGKAN OLEH OWNER\n\n"
        "**CARA SEWA USERBOT (200 MODULES FULL):**\n"
        "Sila buat pembayaran manual terlebih dahulu menggunakan QR Code KIZX STORE. "
        "Selepas bayar, hantar bukti resit kepada Owner dan tunggu kelulusan (Approval) untuk mengaktifkan userbot Anda.\n\n"
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
    user_id = callback_query.from_user.id
    text_pay = (
        "📸 **KIZX STORE MANUAL QR PAYMENT**\n\n"
        "1. Sila scan QR Code di atas dan selesaikan bayaran sewa.\n"
        "2. Selepas berjaya, hantar gambar **Resit Pembayaran (Slip)** di sini sebagai bukti.\n\n"
        "⏳ Sila hantar gambar resit anda sekarang..."
    )
    await callback_query.message.reply_photo(
        photo="https://files.catbox.moe/s1sadp.jpg", 
        caption=text_pay
    )
    
    @bot.on_message(filters.user(user_id) & filters.photo, group=3)
    async def get_receipt(cl, msg):
        await msg.reply("⏳ **Resit dihantar!** Menunggu pengesahan dan kelulusan daripada Owner Utama...")
        
        owner_buttons = [
            [
                InlineKeyboardButton("✅ APPROVE USER", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ REJECT USER", callback_data=f"reject_{user_id}")
            ]
        ]
        await bot.send_photo(
            chat_id=OWNER_ID,
            photo=msg.photo.file_id,
            caption=f"🔔 **BUKTI PEMBAYARAN BARU**\n\n👤 Nama: {msg.from_user.first_name}\n🆔 ID: `{user_id}`\n\nSila semak akaun anda kemudian tekan butang kelulusan di bawah:",
            reply_markup=InlineKeyboardMarkup(owner_buttons)
        )
        await create_payment(user_id, msg.id)
        bot.remove_handler(get_receipt, group=3)

@bot.on_callback_query(filters.regex("approve_") | filters.regex("reject_"))
async def approval_logic(client, callback_query):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("❌ Anda bukan owner utama!", show_alert=True)
        
    action, target_user_id = callback_query.data.split("_")
    target_user_id = int(target_user_id)
    
    if action == "approve":
        await update_payment_status(target_user_id, "approved")
        await callback_query.message.edit_caption("✅ **Pengguna Berhasil Diluluskan (Approved)!**")
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text="🎉 **PEMBAYARAN ANDA TELAH DILULUSKAN (APPROVED)!**\n\n"
                     "Anda kini mempunyai akses penuh untuk menggunakan **200+ Modul Premium**.\n"
                     "Sila klik semula `/start` dan tekan butang **🦅 BUAT USERBOT 🦅** untuk memasukkan string session anda."
            )
        except:
            pass
    else:
        await update_payment_status(target_user_id, "rejected")
        await callback_query.message.edit_caption("❌ **Pengguna Ditolak (Rejected)!**")
        try:
            await bot.send_message(
                chat_id=target_user_id,
                text="❌ **Maaf, Resit Pembayaran Anda Ditolak oleh Owner.**\nSila hubungi support jika ini adalah kesilapan."
            )
        except:
            pass

@bot.on_callback_query(filters.regex("buat_ubot"))
async def buat_ubot_handler(client, callback_query):
    user_id = callback_query.from_user.id
    pay_data = await get_payment(user_id)
    
    if not pay_data or pay_data.get("status") != "approved":
        return await callback_query.answer("⚠️ Akses ditolak! Anda perlu membuat pembayaran dan mendapat kelulusan (Approved) daripada Owner terlebih dahulu.", show_alert=True)
        
    await callback_query.message.edit_text(
        "🔑 **SISTEM PREMIUM MULTI-DEVICE**\n\n"
        "Sila hantar **Pyrogram String Session** anda sekarang untuk mengaktifkan userbot premium dengan 200 module lengkap."
    )
    
    @bot.on_message(filters.user(user_id) & filters.text, group=4)
    async def capture_session(cl, msg):
        session_str = msg.text
        status_msg = await msg.reply("⏳ Menghubungkan pelayan multi-device dan memasang 200 modul premium...")
        
        try:
            new_ubot = Client(f"ubot_{user_id}", api_id=API_ID, api_hash=API_HASH, session_string=session_str)
            await new_ubot.start()
            
            load_plugins_into_ubot(new_ubot)
            await add_ubot(user_id, session_str)
            running_ubots[user_id] = new_ubot
            
            await status_msg.edit(
                "✅ **USERBOT PREMIUM ANDA LENGKAP 200+ MODULE BERJAYA DIAKTIFKAN!**\n\n"
                "Semua pengguna boleh melihat dan menggunakannya.\n"
                "Cuba taip `.alive`, `.testcfd` atau `.gcast [teks]` di mana-mana ruang bualan Telegram."
            )
        except Exception as e:
            await status_msg.edit(f"❌ **Gagal Mengaktifkan!**\nRalat Sesi: `{str(e)}`\nSila pastikan String Session anda sah.")
            
        bot.remove_handler(capture_session, group=4)

@bot.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def global_broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("Sila reply pada mesej/media untuk dibroadcast.")
    all_users = await get_all_users()
    await message.reply(f"📢 Memulai broadcast global ke {len(all_users)} pengguna...")
    success = 0
    for u_id in all_users:
        if await is_banned(u_id): continue
        try:
            await message.reply_to_message.copy(chat_id=u_id)
            success += 1
            await asyncio.sleep(0.3)
        except:
            continue
    await message.reply(f"✅ Broadcast Selesai. Sukses dikirim ke {success} pengguna.")

@bot.on_message(filters.command("blacklist") & filters.user(OWNER_ID))
async def ban_handler(client, message):
    if len(message.command) < 2: return await message.reply("Guna: `/blacklist [USER_ID]`")
    try:
        target = int(message.command[1])
        await ban_user(target)
        if target in running_ubots:
            await running_ubots[target].stop()
            del running_ubots[target]
            await remove_ubot(target)
        await message.reply(f"🚫 User `{target}` berjaya dimasukkan ke blacklist.")
    except:
        await message.reply("ID pengguna mestilah dalam bentuk angka.")

@bot.on_message(filters.command("unblacklist") & filters.user(OWNER_ID))
async def unban_handler(client, message):
    if len(message.command) < 2: return await message.reply("Guna: `/unblacklist [USER_ID]`")
    try:
        target = int(message.command[1])
        await unban_user(target)
        await message.reply(f"✅ User `{target}` dilepaskan dari blacklist.")
    except:
        await message.reply("ID pengguna mestilah dalam bentuk angka.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(restart_all_ubots())
    except:
        pass
    print("🦅 KIZXPREMUBOT ONLINE!")
    bot.run()
