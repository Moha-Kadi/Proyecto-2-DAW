# Manual de Instalacion - BeinScore

## Requisitos
- Docker y Docker Compose
- Cuenta en MongoDB Atlas (gratuita)
- Cuenta en API-Football (gratuita)

## Instalacion

### 1. Clonar el proyecto
```bash
git clone https://github.com/Moha-Kadi/Proyecto-2-DAW.git
cd Proyecto-2-DAW
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

Editar `.env` con tus claves reales:
- `MONGO_URI`: enlace de MongoDB Atlas
- `JWT_SECRET`: cualquier texto largo y secreto
- `FOOTBALL_API_KEY`: clave de API-Football

### 3. Levantar los servicios
```bash
docker compose up -d
```

Esto arranca: nginx, 3 backends balanceados y el frontend Angular.

### 4. Acceder
- **Web**: http://localhost
- **API docs**: http://localhost/docs
- **Health check**: http://localhost/health

### 5. Crear primer usuario (admin)
Registrarse desde la web en `/registro`. Luego cambiar el rol a `admin` desde MongoDB Atlas.
