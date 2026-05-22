# Importaciones
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routes.auth import router as auth_router
from config.config import db, ALLOWED_ORIGINS
from dependencies.limitador import limitador

# Aplicacion FastAPI
app = FastAPI()

# Rate limiting global
app.state.limiter = limitador
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth_router)

# Endpoints basicos
@app.get("/")
async def root():
    return {"status": "Beinscore API Running"}


@app.get("/health")
async def health_check():
    """Health check: verifica que la API y MongoDB respondan."""
    try:
        await db.command("ping")
        return {"status": "ok", "mongodb": "connected"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "mongodb": "disconnected"},
        )
