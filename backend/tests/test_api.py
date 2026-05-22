# Tests basicos de la API
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from jose import jwt

# Variables de entorno
os.environ["MONGO_URI"] = "mongodb://test:27017/test"
os.environ["ALLOWED_ORIGINS"] = "http://test"
os.environ["JWT_SECRET"] = "clave-secreta-test"

# Evita que falle al importar la app sin MongoDB real
with patch("config.config.AsyncIOMotorClient"):
    from main import app

from fastapi.testclient import TestClient

# Cliente de pruebas para hacer peticiones a la API
cliente = TestClient(app)


# Endpoints basicos

def test_raiz_funciona():
    r = cliente.get("/")
    assert r.status_code == 200


def test_health_funciona():
    with patch("main.db.command"):
        r = cliente.get("/health")
    assert r.status_code == 200


# Registro

def test_registro_cuenta_nueva():
    with patch("routes.auth.buscar_por_email", return_value=None), \
         patch("routes.auth.buscar_por_usuario", return_value=None), \
         patch("routes.auth.crear_usuario") as mock_crear:
        mock_crear.return_value = {
            "_id": "abc123",
            "account": {"username": "juan", "email": "juan@test.com",
                        "avatar_url": "", "is_active": True, "rol": "user"},
            "favorites": {"teams": [], "players": []},
        }
        r = cliente.post("/api/auth/registro", json={
            "account": {"username": "juan", "email": "juan@test.com", "password": "pass123"}
        })
    assert r.status_code == 201


def test_registro_email_repetido():
    with patch("routes.auth.buscar_por_email", return_value={"_id": "x"}):
        r = cliente.post("/api/auth/registro", json={
            "account": {"username": "nuevo", "email": "existe@test.com", "password": "pass123"}
        })
    assert r.status_code == 400


# Login

def test_login_correcto():
    usuario = {
        "_id": "abc123",
        "account": {"username": "juan", "email": "juan@test.com", "avatar_url": "",
                    "hashed_password": "x", "is_active": True, "rol": "user"},
        "favorites": {"teams": [], "players": []},
    }
    with patch("routes.auth.buscar_por_email", return_value=usuario), \
         patch("routes.auth.verificar_contrasenia", return_value=True):
        r = cliente.post("/api/auth/login", json={
            "email": "juan@test.com", "password": "ok"
        })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_password_incorrecta():
    with patch("routes.auth.buscar_por_email", return_value={
        "_id": "x", "account": {"hashed_password": "x", "is_active": True}
    }), \
         patch("routes.auth.verificar_contrasenia", return_value=False):
        r = cliente.post("/api/auth/login", json={
            "email": "x@x.com", "password": "mala"
        })
    assert r.status_code == 401


# Perfil protegido

def test_perfil_sin_token():
    r = cliente.put("/api/auth/perfil", json={"username": "x"})
    assert r.status_code == 403


def test_perfil_con_token():
    usuario = {
        "_id": "abc123",
        "account": {"username": "juan", "email": "juan@test.com",
                    "avatar_url": "", "is_active": True, "rol": "user"},
        "favorites": {"teams": [], "players": []},
    }
    with patch("dependencies.auth.buscar_por_id", return_value=usuario):
        token = jwt.encode(
            {"id": "abc123", "exp": datetime.now(timezone.utc) + timedelta(minutes=60)},
            "clave-secreta-test", algorithm="HS256"
        )
        r = cliente.get("/api/auth/perfil", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["account"]["username"] == "juan"


# Fixtures

def test_fixtures_dashboard():
    """El dashboard de fixtures devuelve 200 con las 5 ligas."""
    partido = {
        "fixture": {"id": 1, "timestamp": 1700000000, "status": {"short": "FT"}},
        "teams": {"home": {"name": "A", "logo": ""}, "away": {"name": "B", "logo": ""}},
        "goals": {"home": 1, "away": 0}, "league": {"name": "Test"}
    }
    with patch("routes.fixtures.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json.return_value = {"response": [partido]}
        mock_get.return_value.raise_for_status.return_value = None
        with patch("routes.fixtures.db.__getitem__") as mock_col:
            mock_col.return_value.count_documents.return_value = 0
            mock_col.return_value.bulk_write.return_value = None
            mock_col.return_value.find.return_value.sort.return_value.to_list.return_value = [partido]
            r = cliente.get("/api/fixtures/dashboard")
    assert r.status_code == 200


def test_fixtures_hoy_o_proximos():
    """El endpoint de partidos devuelve datos para una liga."""
    partido = {
        "fixture": {"id": 1, "timestamp": 1700000000, "status": {"short": "FT"}},
        "teams": {"home": {"name": "A", "logo": ""}, "away": {"name": "B", "logo": ""}},
        "goals": {"home": 1, "away": 0}, "league": {"name": "Test"}
    }
    with patch("routes.fixtures.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json.return_value = {"response": [partido]}
        mock_get.return_value.raise_for_status.return_value = None
        with patch("routes.fixtures.db.__getitem__") as mock_col:
            mock_col.return_value.count_documents.return_value = 0
            mock_col.return_value.bulk_write.return_value = None
            mock_col.return_value.find.return_value.sort.return_value.to_list.return_value = [partido]
            r = cliente.get("/api/fixtures/hoy-o-proximos?id_liga=140")
    assert r.status_code == 200


def test_fixtures_detalle_no_encontrado():
    """Un partido que no existe devuelve 404."""
    with patch("routes.fixtures.db.__getitem__") as mock_col:
        mock_col.return_value.find_one.return_value = None
        r = cliente.get("/api/fixtures/99999")
    assert r.status_code == 404


# Clasificacion

def test_clasificacion_cache():
    """La clasificacion cacheada devuelve 200."""
    with patch("routes.standings.db.standings.find_one") as mock_find:
        mock_find.return_value = {"id_liga": 140, "response": [{"league": {"standings": [[{"rank": 1}]]}}]}
        r = cliente.get("/api/clasificacion?id_liga=140")
    assert r.status_code == 200


def test_clasificacion_sin_cache():
    """Sin cache consulta la API externa."""
    with patch("routes.standings.db.standings.find_one", return_value=None), \
         patch("routes.standings.httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json.return_value = {"response": [{"league": {"standings": [[{"rank": 1}]]}}]}
        mock_get.return_value.raise_for_status.return_value = None
        r = cliente.get("/api/clasificacion?id_liga=140")
    assert r.status_code == 200
