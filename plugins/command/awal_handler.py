import config
from pyrogram import Client, types
from plugins import Helper, Database

non_member_msg = (
    "❌ Kamu belum terdaftar sebagai member.\n"
    "Silakan hubungi admin untuk mendaftar. Biaya: Rp 2000"
)

# Fungsi bantu cek apakah user terdaftar (member atau admin)
async def is_terdaftar(db: Database):
    data = db.get_data_pelanggan()
    return data.status in ["member", "admin"]

async def start_handler(client: Client, msg: types.Message):
    db = Database(msg.from_user.id)
    await db.tambah_databot()

    if not await is_terdaftar(db):
        await msg.reply_text(non_member_msg)
        return

    helper = Helper(client, msg)
    first = msg.from_user.first_name or ""
    last = msg.from_user.last_name or ""
    fullname = first + " " + last if last else first
    username = '@' + msg.from_user.username if msg.from_user.username else 'Tidak ada'
    mention = msg.from_user.mention

    await msg.reply_text(
        text=config.start_msg.format(
            id=msg.from_user.id,
            mention=mention,
            username=username,
            first_name=await helper.escapeHTML(first),
            last_name=await helper.escapeHTML(last),
            fullname=await helper.escapeHTML(fullname),
        ),
        disable_web_page_preview=True
    )

async def status_handler(client: Client, msg: types.Message):
    db = Database(msg.from_user.id)
    if not await is_terdaftar(db):
        await msg.reply_text(non_member_msg)
        return

    helper = Helper(client, msg)
    await helper.status_bot()

async def help_handler(client: Client, msg: types.Message):
    db = Database(msg.from_user.id)
    if not await is_terdaftar(db):
        await msg.reply_text(non_member_msg)
        return

    await msg.reply_text(config.help_msg)
