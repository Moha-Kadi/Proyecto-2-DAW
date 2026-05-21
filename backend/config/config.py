# Importaciones
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Carga el archivo .env en las variables de entorno del sistema
load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:4200")

# Cliente de MongoDB
client = AsyncIOMotorClient(MONGO_URI)
# get_database() sin argumentos usa la BD definida en MONGO_URI
db = client.get_database()
