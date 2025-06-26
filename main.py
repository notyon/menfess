from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import Bot, data, Database
from pyrogram import Client, filters, types
import config

# Fungsi untuk reset menfess (jadwal harian)
async def reset_menfess():
    db = Database(data[0])
    x = await db.reset_menfess()
    await Bot().kirim_pesan(x=str(x))
    print('PESAN PROMOTE BERHASIL DIRESET')

# Scheduler aktif setiap jam 1 pagi
scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
scheduler.add_job(reset_menfess, trigger="cron", hour=1, minute=0)
scheduler.start()

# ------------------ CALLBACK UNMUTE ------------------ #
@Bot.on_callback_query(filters.regex("unmute_saya"))
async def unmute_saya_handler(client: Client, callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await client.get_chat_member(config.channel_1, user_id)
        if member.status in ("member", "administrator", "creator"):
            # Unmute user dari channel_2
            await client.unban_chat_member(config.channel_2, user_id)

            # Edit pesan tombol
            await callback_query.message.edit_text(
                "✅ Kamu sudah bergabung, sekarang kamu bisa kirim pesan!"
            )
        else:
            await callback_query.answer("❌ Kamu belum join channel.", show_alert=True)
    except:
        await callback_query.answer("⚠️ Gagal cek keanggotaan. Pastikan kamu sudah join.", show_alert=True)

# Jalankan bot
Bot().run()
