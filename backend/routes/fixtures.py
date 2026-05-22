# Rutas de partidos: integracion con API-Football v3 y cache en MongoDB
from fastapi import APIRouter, HTTPException, Request
from config.config import db, FOOTBALL_API_KEY
from datetime import datetime, timedelta
from pymongo import UpdateOne
import httpx
from dependencies.limitador import limitador

router = APIRouter(prefix="/api/fixtures", tags=["fixtures"])

# Mapeo de IDs de liga a colecciones en MongoDB
COLECCIONES_LIGAS = {
    39: "fixtures_premier",
    140: "fixtures_laliga",
    78: "fixtures_bundesliga",
    135: "fixtures_seriea",
    61: "fixtures_ligue1",
}


# Partidos de hoy o proximos para una liga
@router.get("/hoy-o-proximos")
@limitador.limit("300/minute")
async def obtener_partidos(request: Request, id_liga: int, fecha: str = None):
    coleccion = db[COLECCIONES_LIGAS.get(id_liga, f"fixtures_league_{id_liga}")]

    try:
        # Carga inicial desde la API si la coleccion esta vacia
        if await coleccion.count_documents({}) == 0:
            # Obtiene los partidos de la temporada actual para la liga desde la API
            async with httpx.AsyncClient(timeout=60.0) as cliente:
                resp = await cliente.get(
                    f"https://v3.football.api-sports.io/fixtures?league={id_liga}&season=2024",
                    headers={"x-apisports-key": FOOTBALL_API_KEY}
                )
                resp.raise_for_status()
                partidos_api = resp.json().get("response", [])
                # Inserta o actualiza los partidos en MongoDB usando bulk_write para eficiencia
                if partidos_api:
                    await coleccion.bulk_write([
                        UpdateOne({"fixture.id": p["fixture"]["id"]}, {"$set": p}, upsert=True)
                        for p in partidos_api
                    ])

        # Fecha base: la que viene del frontend o ahora
        fecha_base = datetime.now()
        if fecha:
            try: fecha_base = datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError: pass

        # Simulacion de temporada: datos 2024 mapeados a fecha actual (-365 dias)
        desfase = timedelta(days=365)
        fecha_bd = fecha_base - desfase

        # Busqueda incremental: recorre hasta 15 dias hacia adelante
        partidos = []
        es_hoy = True
        for dia in range(15):
            dia_bd = fecha_bd + timedelta(days=dia)
            ts_inicio = int(dia_bd.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            cursor = coleccion.find(
                {"fixture.timestamp": {"$gte": ts_inicio, "$lt": ts_inicio + 86400}}
            ).sort("fixture.timestamp", 1)
            partidos = await cursor.to_list(length=100)
            if partidos:
                es_hoy = dia == 0
                break

        # Formatea la fecha de la proxima jornada
        str_proxima = None
        if not es_hoy and partidos:
            ts = partidos[0].get("fixture", {}).get("timestamp", 0)
            str_proxima = (datetime.fromtimestamp(ts) + desfase).strftime("%d/%m/%Y")

        # Procesa los partidos para el frontend
        procesados = []
        for p in partidos:
            info = p.get("fixture", {})
            goles = p.get("goals", {})
            ts = info.get("timestamp", 0)
            estado_api = info.get("status", {}).get("short", "")

            # Traduccion de estados de la API a español
            if estado_api in ("1H", "2H", "HT", "ET", "P", "LIVE"):
                estado = "EN VIVO"
                minuto = info.get("status", {}).get("elapsed")
                goles_vista = goles
            elif estado_api in ("FT", "AET", "PEN"):
                estado = "TERMINADO"
                minuto = None
                goles_vista = goles
            else:
                estado = "POR JUGAR"
                minuto = None
                goles_vista = {"home": 0, "away": 0}

            hora = (datetime.fromtimestamp(ts) + desfase).strftime("%H:%M") if ts else ""

            # Agrega el partido formateado a la lista de resultados
            procesados.append({
                "id": info.get("id"), "teams": p.get("teams"),
                "goals": goles_vista, "status": estado,
                "minute": minuto, "start_time": hora, "league": p.get("league"),
            })

        # Devuelve la respuesta con los partidos y la fecha de la proxima jornada
        return {
            "league_id": id_liga, "es_hoy": es_hoy,
            "fecha_proximos": str_proxima,
            "partidos": procesados if es_hoy else [],
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener partidos")


# Eventos de un partido (goles, tarjetas, cambios)
@router.get("/eventos")
@limitador.limit("180/minute")
async def obtener_eventos(request: Request, id_partido: int):
    # Busca el partido en todas las colecciones de liga
    for nombre in COLECCIONES_LIGAS.values():
        coleccion = db[nombre]
        partido = await coleccion.find_one({"fixture.id": id_partido})
        if partido:
            eventos = partido.get("events", [])
            if eventos:
                return eventos
            # Busca en la API si no estan en cache
            try:
                async with httpx.AsyncClient(timeout=30.0) as cliente:
                    resp = await cliente.get(
                        f"https://v3.football.api-sports.io/fixtures/events?fixture={id_partido}",
                        headers={"x-apisports-key": FOOTBALL_API_KEY}
                    )
                    resp.raise_for_status()
                    eventos_api = resp.json().get("response", [])
                    if eventos_api:
                        await coleccion.update_one({"fixture.id": id_partido}, {"$set": {"events": eventos_api}})
                        return eventos_api
            except Exception:
                pass
            break
    return []


# Estadisticas de un partido
@router.get("/estadisticas")
@limitador.limit("180/minute")
async def obtener_estadisticas(request: Request, id_partido: int):
    # Busca el partido en todas las colecciones de liga
    for nombre in COLECCIONES_LIGAS.values():
        coleccion = db[nombre]
        partido = await coleccion.find_one({"fixture.id": id_partido})
        if partido:
            estadisticas = partido.get("statistics", [])
            if estadisticas:
                return estadisticas
            # Busca en la API si no estan en cache
            try:
                async with httpx.AsyncClient(timeout=30.0) as cliente:
                    resp = await cliente.get(
                        f"https://v3.football.api-sports.io/fixtures/statistics?fixture={id_partido}",
                        headers={"x-apisports-key": FOOTBALL_API_KEY}
                    )
                    resp.raise_for_status()
                    estadisticas_api = resp.json().get("response", [])
                    if estadisticas_api:
                        await coleccion.update_one({"fixture.id": id_partido}, {"$set": {"statistics": estadisticas_api}})
                        return estadisticas_api
            except Exception:
                pass
            break
    return []


# Alineaciones de un partido
@router.get("/alineaciones")
@limitador.limit("180/minute")
async def obtener_alineaciones(request: Request, id_partido: int):
    # Busca el partido en todas las colecciones de liga
    for nombre in COLECCIONES_LIGAS.values():
        coleccion = db[nombre]
        partido = await coleccion.find_one({"fixture.id": id_partido})
        if partido:
            alineaciones = partido.get("lineups", [])
            if alineaciones:
                return alineaciones
            # Busca en la API si no estan en cache  
            try:
                async with httpx.AsyncClient(timeout=30.0) as cliente:
                    resp = await cliente.get(
                        f"https://v3.football.api-sports.io/fixtures/lineups?fixture={id_partido}",
                        headers={"x-apisports-key": FOOTBALL_API_KEY}
                    )
                    resp.raise_for_status()
                    alineaciones_api = resp.json().get("response", [])
                    if alineaciones_api:
                        await coleccion.update_one({"fixture.id": id_partido}, {"$set": {"lineups": alineaciones_api}})
                        return alineaciones_api
            except Exception:
                pass
            break
    return []


# Agrega las 5 ligas en una sola respuesta
@router.get("/dashboard")
@limitador.limit("120/minute")
async def obtener_dashboard(request: Request, fecha: str = None):
    resultados = {}
    for id_liga in COLECCIONES_LIGAS:
        try:
            resultados[str(id_liga)] = await obtener_partidos(request, id_liga, fecha)
        except Exception:
            resultados[str(id_liga)] = {
                "league_id": id_liga, "es_hoy": False,
                "fecha_proximos": None, "partidos": [],
            }
    return resultados


# Detalle de un partido
@router.get("/{id_partido}")
@limitador.limit("180/minute")
async def obtener_detalle(request: Request, id_partido: int):
    # Busca el partido en todas las colecciones de liga
    for nombre in COLECCIONES_LIGAS.values():
        partido = await db[nombre].find_one({"fixture.id": id_partido})
        if partido:
            info = partido.get("fixture", {})
            sede = info.get("venue", {})
            return {
                "id": info.get("id"), "date": info.get("date"),
                "referee": info.get("referee") or "No asignado",
                "venue": {"name": sede.get("name") or "Desconocido", "city": sede.get("city") or "Desconocida"},
                "status": info.get("status", {}).get("long"),
                "short_status": info.get("status", {}).get("short"),
                "teams": partido.get("teams"), "goals": partido.get("goals"),
                "score": partido.get("score"), "league": partido.get("league"),
                "events": partido.get("events", []),
            }
    raise HTTPException(status_code=404, detail="Partido no encontrado")


# Detalle completo con eventos, estadisticas y alineaciones
@router.get("/{id_partido}/completo")
@limitador.limit("180/minute")
async def obtener_detalle_completo(request: Request, id_partido: int):
    detalle = await obtener_detalle(request, id_partido)

    try: detalle["events"] = await obtener_eventos(request, id_partido)
    except Exception: detalle["events"] = []

    try: detalle["statistics"] = await obtener_estadisticas(request, id_partido)
    except Exception: detalle["statistics"] = []

    try: detalle["lineups"] = await obtener_alineaciones(request, id_partido)
    except Exception: detalle["lineups"] = []

    return detalle
