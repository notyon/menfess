from typing import List, Dict
import pymongo
import config
import json

myclient = pymongo.MongoClient(config.db_url)
mydb = myclient[config.db_name]
mycol = mydb['user']

class Database():
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def is_member(self):
        data = mycol.find_one({'_id': self.user_id})
        return data and data.get('status') in ["member", "admin"]

    async def add_member(self):
        mycol.update_one({'_id': self.user_id}, {'$set': {'status': 'member'}}, upsert=True)

    async def remove_member(self):
        mycol.update_one({'_id': self.user_id}, {'$set': {'status': 'non-member'}}, upsert=True)

    async def tambah_databot(self):
        user = mycol.find_one({"_id": self.user_id})
        import config

        if user:
            # Jika admin tapi status belum benar, perbaiki
            if self.user_id in config.admin and user.get("status") != "admin":
                mycol.update_one({"_id": self.user_id}, {"$set": {"status": "admin"}})
            return

        # User baru: admin atau non-member
        status = "admin" if self.user_id in config.admin else "non-member"

        data = {
            "_id": self.user_id,
            "nama": "Pengguna",
            "status": status,
            "coin": f"0_{self.user_id}",
            "menfess": 0,
            "all_menfess": 0,
            "sign_up": True,
            "bot_status": True,
            "ban": {},
            "admin": [],
            "kirimchannel": {
                "photo": True,
                "video": False,
                "voice": False
            }
        }
        await self.tambah_pelanggan(data)

    async def tambah_pelanggan(self, data):
        mycol.insert_one(data)

    def get_data_pelanggan(self):
        found = mycol.find_one({'_id': self.user_id})
        return data_pelanggan(found)

class data_pelanggan():
    def __init__(self, args):
        self.id = args['_id']
        self.nama = str(args.get('nama', ''))
        self.mention = f'<a href="tg://user?id={self.id}">{self.nama}</a>'
        self.coin = int(args.get('coin', f'0_{self.id}').split('_')[0])
        self.coin_full = args.get('coin', f'0_{self.id}')
        self.status = args.get('status', 'non-member').split('_')[0]
        self.status_full = args.get('status', 'non-member')
        self.menfess = int(args.get('menfess', 0))
        self.all_menfess = int(args.get('all_menfess', 0))
        self.sign_up = args.get('sign_up', False)
        self.json = args

    def __str__(self) -> str:
        return str(json.dumps(self.json, indent=3))

# Handler untuk command /status
from pyrogram import Client, filters, types

@Client.on_message(filters.command("status") & filters.private)
async def status_handler(client: Client, msg: types.Message):
    db = Database(msg.from_user.id)
    await db.tambah_databot()

    data = db.get_data_pelanggan()
    if data.status not in ["member", "admin"]:
        return await msg.reply("❌ Kamu belum terdaftar sebagai member.\nSilakan hubungi admin untuk mendaftar.")

    await msg.reply(f"🔍 Status: {data.status}\n🪙 Coin: {data.coin}\n📮 Menfess: {data.menfess}")
    
