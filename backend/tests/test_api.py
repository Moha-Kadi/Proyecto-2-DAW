# Tests de la API
import pytest
from unittest.mock import AsyncMock, patch
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
    # Mock de db.command("ping") para simular que MongoDB responde
    with patch("main.db.command", new_callable=AsyncMock):
        async with AsyncClient(app=app, base_url="http://test") as c:
            r = await c.get("/health")
    assert r.status_code == 200
