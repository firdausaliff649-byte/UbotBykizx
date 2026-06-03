import os
from motor.motor_asyncio import AsyncIOMotorClient

# Menggunakan Environment Variable Mongo atau pangkalan data local default
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["kizx_ubot_db"]

sessions_db = db["sessions"]
blacklist_db = db["blacklist"]
users_db = db["users"]
payments_db = db["payments"]

async def add_ubot(user_id, session):
    await sessions_db.update_one({"user_id": user_id}, {"$set": {"session": session}}, upsert=True)

async def remove_ubot(user_id):
    await sessions_db.delete_one({"user_id": user_id})

async def get_all_ubots():
    cursor = sessions_db.find({})
    return await cursor.to_list(length=1000)

async def is_banned(user_id):
    user = await blacklist_db.find_one({"user_id": user_id})
    return True if user else False

async def ban_user(user_id):
    await blacklist_db.update_one({"user_id": user_id}, {"$set": {"banned": True}}, upsert=True)

async def unban_user(user_id):
    await blacklist_db.delete_one({"user_id": user_id})

async def add_user(user_id):
    await users_db.update_one({"user_id": user_id}, {"$set": {"active": True}}, upsert=True)

async def get_all_users():
    cursor = users_db.find({})
    results = await cursor.to_list(length=5000)
    return [doc["user_id"] for doc in results]

async def create_payment(user_id, message_id):
    await payments_db.update_one(
        {"user_id": user_id},
        {"$set": {"message_id": message_id, "status": "pending"}},
        upsert=True
    )

async def get_payment(user_id):
    return await payments_db.find_one({"user_id": user_id})

async def update_payment_status(user_id, status):
    await payments_db.update_one({"user_id": user_id}, {"$set": {"status": status}})
