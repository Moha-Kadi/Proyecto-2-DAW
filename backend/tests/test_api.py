# Tests basicos de la API
import os
from unittest.mock import patch

# Variables de entorno
os.environ["MONGO_URI"] = "mongodb://test:27017/test"
os.environ["ALLOWED_ORIGINS"] = "http://test"

# Evita que falle al importar la app sin MongoDB real
with patch("config.config.AsyncIOMotorClient"):
    from main import app

from fastapi.testclient import TestClient

cliente = TestClient(app)


def test_raiz_funciona():
    """La raiz responde con mensaje de bienvenida."""
    r = cliente.get("/")
    assert r.status_code == 200


def test_health_funciona():
    """El health check responde ok."""
    with patch("main.db.command"):
        r = cliente.get("/health")
    assert r.status_code == 200
