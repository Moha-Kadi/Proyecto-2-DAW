# Valida el token JWT y devuelve el usuario actual
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.config import JWT_ALGORITHM, JWT_SECRET
from models.user import buscar_por_id

# Esquema de seguridad Bearer para extraer el token de la cabecera Authorization
seguridad = HTTPBearer()


# Dependencia que valida el token y devuelve el usuario de la base de datos
async def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(seguridad),
) -> dict:
    error_autenticacion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales no validas o sesion expirada"
    )

    try:
        # Decodificar el token JWT
        token = credenciales.credentials
        datos_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Extraer el ID del usuario del token
        id_usuario: str = datos_token.get("id")
        if id_usuario is None:
            raise error_autenticacion

        # Buscar el usuario en la base de datos
        usuario = await buscar_por_id(id_usuario)
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Comprobar si la cuenta esta activa
        if not usuario.get("account", {}).get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta cuenta esta desactivada"
            )

        return usuario

    except JWTError:
        raise error_autenticacion
