# Tests basicos de la API
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Variables de entorno para tests
os.environ["MONGO_URI"] = "mongodb://test:27017/test"
os.environ["JWT_SECRET"] = "test"
os.environ["ALLOWED_ORIGINS"] = "http://test"

# Mock de MongoDB para no necesitar conexion real
db_falsa = MagicMock()
db_falsa.command = AsyncMock()
cliente_falso = MagicMock()
cliente_falso.get_database.return_value = db_falsa
patch("config.config.AsyncIOMotorClient", return_value=cliente_falso).start()

import pytest
from httpx import AsyncClient
from main import app


# Endpoint raiz
@pytest.mark.asyncio
async def test_raiz_funciona():
    """La raiz responde con mensaje de bienvenida."""
    async with AsyncClient(app=app, base_url="http://test") as c:
        r = await c.get("/")
    assert r.status_code == 200


# Health check y conexion a MongoDB
@pytest.mark.asyncio
async def test_health_funciona():
    """El health check responde ok y verifica la conexion a MongoDB."""
    with patch("main.db.command", new_callable=AsyncMock):
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get("/health")
    assert r.status_code == 200
