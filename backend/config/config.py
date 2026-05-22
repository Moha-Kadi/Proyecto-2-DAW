# Configuracion global: variables de entorno, MongoDB, JWT, CORS
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Carga el archivo .env
load_dotenv()

# MongoDB
MONGO_URI = os.environ["MONGO_URI"]
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database()

# JWT
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

# CORS
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:4200")

# API externa
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY", "")
