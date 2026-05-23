# Documentacion Tecnica - BeinScore

## Stack tecnologico
- Backend: Python 3.12 + FastAPI
- Frontend: Angular 21 + Tailwind CSS
- Base de datos: MongoDB (Atlas)
- Proxy inverso: Nginx (balanceo round-robin)
- Contenedores: Docker + Docker Compose

## Estructura del proyecto
- `backend/` — API REST
- `frontend/` — SPA Angular
- `nginx/` — configuracion proxy inverso
- `docs/` — documentacion
- `docker-compose.yml` — orquestacion

## Endpoints de la API
- **Auth**: POST /registro, POST /login, GET/PUT /perfil
- **Fixtures**: GET /dashboard, /hoy-o-proximos, /eventos, /estadisticas, /alineaciones, /detalle
- **Standings**: GET /clasificacion
- **Admin**: GET /usuarios, PUT /toggle, DELETE /usuario

## Modelo de datos
- **users**: account (username, email, hashed_password, avatar_url, is_active, rol), favorites
- **standings**: datos de clasificacion cacheados por liga
- **fixtures_***: partidos cacheados por liga (5 colecciones)

## Arquitectura
Nginx (puerto 80) → /api/* → backend pool (3 replicas balanceadas)
                    → /docs, /openapi.json → backend
                    → resto → frontend Angular (puerto 4200)

## Autenticacion
JWT con algoritmo HS256. El token viaja en `Authorization: Bearer <token>`. El middleware valida el token en cada peticion protegida.

## Variables de entorno
MONGO_URI, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, ALLOWED_ORIGINS, FOOTBALL_API_KEY

## Despliegue
```bash
docker compose up -d
```
Servicios: nginx (80), backend1/2/3, frontend-dev
