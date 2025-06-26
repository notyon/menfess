
from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.database.database import Database
import config

@Client.on_message(filters.command("daftar") & filters.user(config.admin))
async def daftar_handler(client: Client, msg: Message):
    if len(msg.command) < 2:
        await msg.reply("Gunakan: /daftar [user_id]")
        return
    try:
        user_id = int(msg.command[1])
        db = Database(user_id)
        await db.add_member()
        await msg.reply(f"✅ User {user_id} sekarang adalah member.")
    except Exception as e:
        await msg.reply(f"Terjadi kesalahan: {e}")

@Client.on_message(filters.command("remove") & filters.user(config.admin))
async def remove_handler(client: Client, msg: Message):
    if len(msg.command) < 2:
        await msg.reply("Gunakan: /remove [user_id]")
        return
    try:
        user_id = int(msg.command[1])
        db = Database(user_id)
        await db.remove_member()
        await msg.reply(f"❌ User {user_id} sekarang bukan member.")
    except Exception as e:
        await msg.reply(f"Terjadi kesalahan: {e}")
