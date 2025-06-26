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
    if msg.chat.type == enums.ChatType.PRIVATE:
        if msg.from_user is None:
            return

        uid = msg.from_user.id
        helper = Helper(client, msg)
        database = Database(uid)

        # Cek langganan channel
        if not await helper.cek_langganan_channel(uid):
            return await helper.pesan_langganan()

        if not await database.cek_user_didatabase():
            await helper.daftar_pelanggan()
            await helper.send_to_channel_log(type="log_daftar")

        if not database.get_data_bot(client.id_bot).bot_status:
            status = ['member', 'banned']
            member = database.get_data_pelanggan()
            if member.status in status:
                return await client.send_message(uid, "<i>Saat ini bot sedang dinonaktifkan</i>", enums.ParseMode.HTML)

        command = msg.text or msg.caption

        if command:
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
                member = database.get_data_pelanggan()
                if member.status in ['admin', 'owner']:
                    return await setting_handler(client, msg)
            elif re.search(r"^[\/]{1}tf_coin", command):
                return await transfer_coin_handler(client, msg)
            elif re.search(r"^[\/]{1}bot", command):
                if uid == config.id_admin:
                    return await bot_handler(client, msg)
            elif re.search(r"^[\/]{1}admin", command):
                if uid == config.id_admin:
                    return await tambah_admin_handler(client, msg)
            elif re.search(r"^[\/]{1}unadmin", command):
                if uid == config.id_admin:
                    return await hapus_admin_handler(client, msg)
            elif re.search(r"^[\/]{1}ban", command):
                member = database.get_data_pelanggan()
                if member.status in ['admin', 'owner']:
                    return await ban_handler(client, msg)
            elif re.search(r"^[\/]{1}unban", command):
                member = database.get_data_pelanggan()
                if member.status in ['admin', 'owner']:
                    return await unban_handler(client, msg)

            # Deteksi hashtag
            x = re.search(fr"(?:^|\s)({config.hastag})", command.lower())
            if x:
                key = x.group(1)
                hastag = config.hastag.split('|')
                member = database.get_data_pelanggan()

                if member.status == 'banned':
                    return await msg.reply(f'Kamu telah <b>di banned</b>\n\n<u>Alasan:</u> {database.get_data_bot(client.id_bot).ban[str(uid)]}\nsilahkan kontak admin @xvilance untuk unbanned', True, enums.ParseMode.HTML)

                if key in hastag:
                    if key == command.lower() or len(command.split(' ')) < 3:
                        return await msg.reply('\ud83d\ude45\u200d\u2640\ufe0f  post gagal terkirim, <b>mengirim pesan wajib lebih dari 3 kata.</b>', True, enums.ParseMode.HTML)
                    else:
                        return await send_menfess_handler(client, msg)
                else:
                    await gagal_kirim_handler(client, msg)
            else:
                await gagal_kirim_handler(client, msg)

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
                await query.answer('Ditolak, kamu tidak ada akses', True)
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
