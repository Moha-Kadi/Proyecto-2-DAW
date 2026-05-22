# Clasificaciones de ligas: cache-first con API-Football v3
from fastapi import APIRouter, HTTPException, Request
from config.config import db, FOOTBALL_API_KEY
from dependencies.limitador import limitador
import httpx

router = APIRouter(prefix="/api/clasificacion", tags=["clasificacion"])


# Obtiene la clasificacion de una liga
@router.get("/")
@limitador.limit("120/minute")
async def obtener_clasificacion(request: Request, id_liga: int):
    # Busca primero en la cache de MongoDB
    cache = await db.standings.find_one({"id_liga": id_liga})
    # Borramos id debido a que ObjectId no se puede convertir a json
    if cache:
        cache.pop("_id", None)
        return cache

    # Si no esta en cache, consulta la API externa
    url = f"https://v3.football.api-sports.io/standings?league={id_liga}&season=2024"
    cabeceras = {"x-apisports-key": FOOTBALL_API_KEY}

    try:
        # Consulta a la API externa con httpx y maneja posibles errores
        async with httpx.AsyncClient(timeout=10.0) as cliente:
            resp = await cliente.get(url, headers=cabeceras)
            resp.raise_for_status()
            datos = resp.json()

            # Si la API externa devuelve un error, no guardamos nada en cache y devolvemos un error 502
            if datos.get("errors"):
                raise HTTPException(status_code=502, detail="Error del proveedor de datos")

            # Guarda en base de datos solo si la respuesta es correcta
            if datos.get("response"):
                datos["id_liga"] = id_liga
                await db.standings.insert_one(datos)

            return datos
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener la clasificacion")
