import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:4200")

client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database()
