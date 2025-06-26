import re
from pyrogram import Client, filters, enums, types
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import config
from plugins import Database, Helper
from plugins.command import *
from bot import Bot

# Handler untuk pesan privat
@Bot.on_message()
async def on_message(client: Client, msg: Message):
    if msg.chat.type != enums.ChatType.PRIVATE or msg.from_user is None:
        return

    uid = msg.from_user.id
    helper = Helper(client, msg)
    database = Database(uid)

    # Cek langganan channel
    if not await helper.cek_langganan_channel(uid):
        return await helper.pesan_langganan()

    # Cek dan daftar user jika belum ada di database
    if not await database.cek_user_didatabase():
        await database.tambah_databot()
        await helper.send_to_channel_log(type="log_daftar")

    member = database.get_data_pelanggan()

    # Cek status bot (dari data pengguna, bukan get_data_bot)
    if not member.json.get("bot_status", True):
        if member.status in ['member', 'banned']:
            return await client.send_message(uid, "<i>Saat ini bot sedang dinonaktifkan</i>", enums.ParseMode.HTML)

    command = msg.text or msg.caption
    if not command:
        return

    # ======== Command Handler =========
    if command == '/start':
        return await start_handler(client, msg)
    elif command == '/help':
        return await help_handler(client, msg)
    elif command == '/status':
        return await status_handler(client, msg)
    elif command == '/list_admin':
        return await list_admin_handler(helper, client.id_bot)
    elif command == '/list_ban':
        return await list_ban_handler(helper, client.id_bot)
    elif command == '/stats':
        if uid == config.id_admin:
            return await statistik_handler(helper, client.id_bot)
    elif command == '/broadcast':
        if uid == config.id_admin:
            return await broadcast_handler(client, msg)
    elif command in ['/settings', '/setting']:
        if member.status in ['admin', 'owner']:
            return await setting_handler(client, msg)
    elif re.match(r"^/tf_coin", command):
        return await transfer_coin_handler(client, msg)
    elif re.match(r"^/bot", command):
        if uid == config.id_admin:
            return await bot_handler(client, msg)
    elif re.match(r"^/admin", command):
        if uid == config.id_admin:
            return await tambah_admin_handler(client, msg)
    elif re.match(r"^/unadmin", command):
        if uid == config.id_admin:
            return await hapus_admin_handler(client, msg)
    elif re.match(r"^/ban", command):
        if member.status in ['admin', 'owner']:
            return await ban_handler(client, msg)
    elif re.match(r"^/unban", command):
        if member.status in ['admin', 'owner']:
            return await unban_handler(client, msg)

    # ======== Deteksi Hashtag untuk Menfess =========
    x = re.search(fr"(?:^|\s)({config.hastag})", command.lower())
    if x:
        key = x.group(1)
        hastag_list = config.hastag.split('|')

        if member.status == 'banned':
            alasan = member.json.get("ban", {}).get(str(uid), "tidak diketahui")
            return await msg.reply(
                f'Kamu telah <b>di banned</b>\n\n<u>Alasan:</u> {alasan}\nSilakan kontak admin @xvilance untuk unbanned',
                parse_mode=enums.ParseMode.HTML
            )

        if key in hastag_list:
            if key == command.lower() or len(command.split(' ')) < 3:
                return await msg.reply(
                    '🙅‍♀️ Post gagal terkirim, <b>mengirim pesan wajib lebih dari 3 kata.</b>',
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                return await send_menfess_handler(client, msg)

    # Jika tidak sesuai
    await gagal_kirim_handler(client, msg)


async def gagal_kirim_handler(client, msg):
    await msg.reply("🚫 Kamu tidak diizinkan mengakses fitur ini. Harap hubungi admin jika kamu merasa ini kesalahan.")


# Handler callback tombol
@Bot.on_callback_query()
async def on_callback_query(client: Client, query: CallbackQuery):
    try:
        data = query.data

        if data == 'photo':
            await photo_handler_inline(client, query)
        elif data == 'video':
            await video_handler_inline(client, query)
        elif data == 'voice':
            await voice_handler_inline(client, query)
        elif data == 'status_bot':
            if query.message.chat.id == config.id_admin:
                await status_handler_inline(client, query)
            else:
                await query.answer('Ditolak, kamu tidak ada akses', show_alert=True)
        elif data == 'ya_confirm':
            await broadcast_ya(client, query)
        elif data == 'tidak_confirm':
            await close_cbb(client, query)
        elif data == 'unmute_saya':
            user_id = query.from_user.id
            try:
                member = await client.get_chat_member(config.channel_1, user_id)
                if member.status in ["member", "administrator", "creator"]:
                    await client.unban_chat_member(config.channel_2, user_id)
                    await query.message.edit_text("✅ Kamu sudah bergabung, sekarang kamu bisa kirim pesan!")
                else:
                    await query.answer("❌ Kamu belum join channel.", show_alert=True)
            except:
                await query.answer("⚠️ Gagal cek. Mungkin kamu belum join?", show_alert=True)
    except:
        pass


# Cek otomatis keanggotaan user di channel 1 saat kirim pesan ke channel 2
@Bot.on_message(filters.chat(config.channel_2))
async def cek_keanggotaan_channel(client: Client, msg: Message):
    if msg.from_user is None:
        return

    user_id = msg.from_user.id
    try:
        member = await client.get_chat_member(config.channel_1, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            raise Exception("Not a member")
    except:
        await client.restrict_chat_member(
            config.channel_2,
            user_id,
            permissions=types.ChatPermissions()
        )

        await msg.reply(
            config.pesan_join,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Unmute saya", callback_data="unmute_saya")]
            ])
        )
