# Configuracion global de pytest para los tests
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Añade el directorio padre al path para que los imports funcionen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Variables de entorno para tests (evita depender del .env real)
os.environ["MONGO_URI"] = "mongodb://test:27017/test"
os.environ["JWT_SECRET"] = "clave-secreta-test"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "60"
os.environ["ALLOWED_ORIGINS"] = "http://test"
os.environ["FOOTBALL_API_KEY"] = "api-key-test"

# Mock de la conexion a MongoDB para no necesitar una BD real durante los tests
db_falsa = MagicMock()
db_falsa.command = AsyncMock()
cliente_falso = MagicMock()
cliente_falso.get_database.return_value = db_falsa
patch("config.config.AsyncIOMotorClient", return_value=cliente_falso).start()
