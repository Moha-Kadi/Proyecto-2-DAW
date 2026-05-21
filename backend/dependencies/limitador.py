# Importaciones
from slowapi import Limiter
from slowapi.util import get_remote_address

# Limita todas las rutas a 200 peticiones por minuto por IP
limitador = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
