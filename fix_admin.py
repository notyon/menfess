from pymongo import MongoClient

# Ganti ini sesuai config.py kamu
mongo_url = "mongodb://localhost:27017/"
db_name = "menfessztest"

client = MongoClient(mongo_url)
db = client[db_name]
user_col = db["user"]

admin_id = 732448606  # Ganti dengan ID admin kamu

# Update status admin langsung
user_col.update_one({"_id": admin_id}, {"$set": {"status": "member"}})

print("✅ Admin status berhasil diperbarui ke 'member'")
