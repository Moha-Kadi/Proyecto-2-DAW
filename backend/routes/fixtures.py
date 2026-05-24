# Rutas de partidos: integracion con API-Football v3 y cache en MongoDB
from fastapi import APIRouter, HTTPException, Request
from config.config import db, FOOTBALL_API_KEY
from datetime import datetime, timedelta
from pymongo import UpdateOne
import httpx
from dependencies.limitador import limitador

router = APIRouter(prefix="/api/fixtures", tags=["fixtures"])

# Mapeo: cada liga tiene su propia coleccion en MongoDB
COLECCIONES_LIGAS = {
    39: "fixtures_premier",
    140: "fixtures_laliga",
    78: "fixtures_bundesliga",
    135: "fixtures_seriea",
    61: "fixtures_ligue1",
}


# Devuelve los partidos de una liga para un dia concreto.
# Si no hay partidos ese dia, busca hasta 15 dias hacia adelante (proxima jornada).
# Usa datos de la temporada 2024 y los simula como si fueran de la fecha actual (-365 dias).
@router.get("/hoy-o-proximos")
@limitador.limit("300/minute")
async def obtener_partidos(request: Request, id_liga: int, fecha: str = None):
    # Selecciona la coleccion MongoDB para esta liga
    coleccion = db[COLECCIONES_LIGAS.get(id_liga, f"fixtures_league_{id_liga}")]

    try:
        # Carga inicial: Descarga todos los partidos de la temporada 2024 desde API-Football
        # y los guarda en MongoDB con bulk_write + upsert
        if await coleccion.count_documents({}) == 0:
            async with httpx.AsyncClient(timeout=60.0) as cliente:
                resp = await cliente.get(
                    f"https://v3.football.api-sports.io/fixtures?league={id_liga}&season=2024",
                    headers={"x-apisports-key": FOOTBALL_API_KEY}
                )
                resp.raise_for_status()
                partidos_api = resp.json().get("response", [])
                if partidos_api:
                    # bulk_write: inserta todos los partidos de golpe 
                    # upsert=True: si ya existe un partido con ese fixture.id, lo actualiza
                    await coleccion.bulk_write([
                        UpdateOne({"fixture.id": p["fixture"]["id"]}, {"$set": p}, upsert=True)
                        for p in partidos_api
                    ])

        # Si el frontend envia una fecha, se usa esa. Si no, se usa la fecha actual.
        fecha_base = datetime.now()
        if fecha:
            try: fecha_base = datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError: pass

        # restamos 365 dias a la fecha actual y buscamos en 2024.
        desfase = timedelta(days=365)
        fecha_bd = fecha_base - desfase

        # Busca partidos desde la fecha dada hasta 15 dias hacia adelante para encontrar la proxima jornada.
        partidos = []
        es_hoy = True
        for dia in range(15):
            dia_bd = fecha_bd + timedelta(days=dia)
            # Convierte la fecha a timestamp 
            # replace() pone la hora a 00:00:00 para abarcar todo el dia
            ts_inicio = int(dia_bd.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            # Busca partidos cuyo timestamp este entre las 00:00 y las 23:59 de ese dia
            cursor = coleccion.find(
                {"fixture.timestamp": {"$gte": ts_inicio, "$lt": ts_inicio + 86400}}
            ).sort("fixture.timestamp", 1)
            partidos = await cursor.to_list(length=100)
            # Si encuentra partidos, sale del bucle. Si no, sigue buscando en los dias siguientes.
            if partidos:
                es_hoy = dia == 0  
                break

        # Si no es hoy (partidos futuros), calcula la fecha real sumando el desfase
        str_proxima = None
        if not es_hoy and partidos:
            ts = partidos[0].get("fixture", {}).get("timestamp", 0)
            str_proxima = (datetime.fromtimestamp(ts) + desfase).strftime("%d/%m/%Y")

        # Convierte los datos crudos de la API en un formato mas limpio
        procesados = []
        for p in partidos:
            info = p.get("fixture", {})
            goles = p.get("goals", {})
            ts = info.get("timestamp", 0)
            estado_api = info.get("status", {}).get("short", "")

            # Traduce los codigos de estado de la API a español
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

            # Convierte el timestamp a hora local sumando el desfase
            hora = (datetime.fromtimestamp(ts) + desfase).strftime("%H:%M") if ts else ""

            # Agrega el partido procesado a la lista de resultados
            procesados.append({
                "id": info.get("id"), "teams": p.get("teams"),
                "goals": goles_vista, "status": estado,
                "minute": minuto, "start_time": hora, "league": p.get("league"),
            })

        # Si es hoy, devuelve los partidos. Si son proximos, partidos vacio
        # y el frontend usa fecha_proximos para mostrar el aviso.
        return {
            "league_id": id_liga, "es_hoy": es_hoy,
            "fecha_proximos": str_proxima,
            "partidos": procesados if es_hoy else [],
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al obtener partidos")


# Devuelve los eventos de un partido (goles, tarjetas, cambios).
@router.get("/eventos")
@limitador.limit("180/minute")
async def obtener_eventos(request: Request, id_partido: int):
    # Recorre las 5 colecciones de liga hasta encontrar el partido
    for nombre in COLECCIONES_LIGAS.values():
        coleccion = db[nombre]
        partido = await coleccion.find_one({"fixture.id": id_partido})
        if partido:
            # Si el partido ya tiene eventos guardados, los devuelve directamente
            eventos = partido.get("events", [])
            if eventos:
                return eventos
            # Si no, consulta la API externa y los guarda para la proxima
            try:
                async with httpx.AsyncClient(timeout=30.0) as cliente:
                    resp = await cliente.get(
                        f"https://v3.football.api-sports.io/fixtures/events?fixture={id_partido}",
                        headers={"x-apisports-key": FOOTBALL_API_KEY}
                    )
                    resp.raise_for_status()
                    eventos_api = resp.json().get("response", [])
                    if eventos_api:
                        # $set guarda los eventos dentro del documento del partido
                        await coleccion.update_one({"fixture.id": id_partido}, {"$set": {"events": eventos_api}})
                        return eventos_api
            except Exception:
                pass
            break
    return []


# Devuelve las estadisticas de un partido
@router.get("/estadisticas")
@limitador.limit("180/minute")
async def obtener_estadisticas(request: Request, id_partido: int):
    for nombre in COLECCIONES_LIGAS.values():
        coleccion = db[nombre]
        partido = await coleccion.find_one({"fixture.id": id_partido})
        if partido:
            estadisticas = partido.get("statistics", [])
            if estadisticas:
                return estadisticas
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


# Devuelve las alineaciones de un partido
@router.get("/alineaciones")
@limitador.limit("180/minute")
async def obtener_alineaciones(request: Request, id_partido: int):
    for nombre in COLECCIONES_LIGAS.values():
        coleccion = db[nombre]
        partido = await coleccion.find_one({"fixture.id": id_partido})
        if partido:
            alineaciones = partido.get("lineups", [])
            if alineaciones:
                return alineaciones
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


# Devuelve el dashboard con los partidos de hoy o, si no hay, los proximos partidos de cada liga.
@router.get("/dashboard")
@limitador.limit("120/minute")
async def obtener_dashboard(request: Request, fecha: str = None):
    resultados = {}
    for id_liga in COLECCIONES_LIGAS:
        try:
            # Llama a obtener_partidos para cada liga
            resultados[str(id_liga)] = await obtener_partidos(request, id_liga, fecha)
        except Exception:
            # Si una liga falla, devuelve vacio para esa liga sin romper las demas
            resultados[str(id_liga)] = {
                "league_id": id_liga, "es_hoy": False,
                "fecha_proximos": None, "partidos": [],
            }
    return resultados


# Devuelve informacion de un partido
@router.get("/{id_partido}")
@limitador.limit("180/minute")
async def obtener_detalle(request: Request, id_partido: int):
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


# Devuelve el detalle completo de un partido, incluyendo eventos, estadisticas y alineaciones.
@router.get("/{id_partido}/completo")
@limitador.limit("180/minute")
async def obtener_detalle_completo(request: Request, id_partido: int):
    # Obtiene el detalle base (equipos, resultado, estadio...)
    detalle = await obtener_detalle(request, id_partido)

    # Añade eventos, estadisticas y alineaciones
    # Cada uno puede fallar sin romper el resto
    try: detalle["events"] = await obtener_eventos(request, id_partido)
    except Exception: detalle["events"] = []

    try: detalle["statistics"] = await obtener_estadisticas(request, id_partido)
    except Exception: detalle["statistics"] = []

    try: detalle["lineups"] = await obtener_alineaciones(request, id_partido)
    except Exception: detalle["lineups"] = []

    return detalle
