# Rutas de autenticacion: registro, login, perfil y creacion de admin
from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import datetime, timedelta, timezone
from jose import jwt

from schemas.user import (
    CrearUsuario,
    RespuestaUsuario,
    IniciarSesion,
    RespuestaToken,
    RespuestaCuenta,
    Favoritos,
    ActualizarCuenta,
)
from models.user import (
    crear_usuario,
    buscar_por_email,
    buscar_por_usuario,
    verificar_contrasenia,
    actualizar_cuenta,
    buscar_por_id,
)
from config.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from dependencies.auth import obtener_usuario_actual
from dependencies.limitador import limitador

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])


# Registro de nuevo usuario
@router.post("/registro", response_model=RespuestaUsuario, status_code=status.HTTP_201_CREATED)
@limitador.limit("120/minute")
async def registrar(request: Request, datos_usuario: CrearUsuario):
    # Verificar si el email ya esta registrado
    email_existente = await buscar_por_email(datos_usuario.account.email)
    if email_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya esta registrado",
        )

    # Verificar si el nombre de usuario ya esta registrado
    nombre_usuario_existente = await buscar_por_usuario(datos_usuario.account.username)
    if nombre_usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya esta en uso",
        )

    # Crear el usuario en la base de datos
    diccionario_cuenta = datos_usuario.account.model_dump()
    usuario = await crear_usuario(diccionario_cuenta)

    return RespuestaUsuario(
        id=usuario["_id"],
        account=RespuestaCuenta(
            username=usuario["account"]["username"],
            email=usuario["account"]["email"],
            avatar_url=usuario["account"]["avatar_url"],
            is_active=usuario["account"]["is_active"],
            rol=usuario["account"]["rol"],
        ),
        favorites=Favoritos(teams=usuario["favorites"]["teams"], players=usuario["favorites"]["players"]),
    )


# Inicio de sesion
@router.post("/login", response_model=RespuestaToken)
@limitador.limit("120/minute")
async def login(request: Request, datos_acceso: IniciarSesion):
    # Buscar el usuario por email
    usuario = await buscar_por_email(datos_acceso.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasenia incorrectos",
        )

    # Verificar la contrasenia
    contrasenia_valida = verificar_contrasenia(datos_acceso.password, usuario["account"]["hashed_password"])
    if not contrasenia_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasenia incorrectos",
        )

    # Verificar si la cuenta esta activa
    if not usuario["account"]["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada")

    # Crear el token JWT
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    datos_token = {
        "id": usuario["_id"],
        "email": usuario["account"]["email"],
        "exp": expiracion,
    }
    token_acceso = jwt.encode(datos_token, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return RespuestaToken(
        access_token=token_acceso,
        token_type="bearer",
        user=RespuestaUsuario(
            id=usuario["_id"],
            account=RespuestaCuenta(
                username=usuario["account"]["username"],
                email=usuario["account"]["email"],
                avatar_url=usuario["account"]["avatar_url"],
                is_active=usuario["account"]["is_active"],
                rol=usuario["account"]["rol"],
            ),
            favorites=Favoritos(
                teams=usuario["favorites"]["teams"], players=usuario["favorites"]["players"]
            ),
        ),
    )


# Perfil del usuario autenticado
@router.get("/perfil", response_model=RespuestaUsuario)
async def obtener_perfil(usuario_actual: dict = Depends(obtener_usuario_actual)):
    return RespuestaUsuario(
        id=usuario_actual["_id"],
        account=RespuestaCuenta(
            username=usuario_actual["account"]["username"],
            email=usuario_actual["account"]["email"],
            avatar_url=usuario_actual["account"]["avatar_url"],
            is_active=usuario_actual["account"]["is_active"],
            rol=usuario_actual["account"]["rol"],
        ),
        favorites=Favoritos(
            teams=usuario_actual["favorites"]["teams"],
            players=usuario_actual["favorites"]["players"],
        ),
    )


# Actualizar perfil del usuario autenticado
@router.put("/perfil", response_model=RespuestaUsuario)
async def actualizar_perfil(
    datos_cuenta: ActualizarCuenta,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    id_usuario_actual = usuario_actual["_id"]
    actualizaciones = {}

    # Cambio de contrasenia
    if datos_cuenta.password:
        if not datos_cuenta.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere contrasenia actual para cambiar password",
            )
        contrasenia_valida = verificar_contrasenia(
            datos_cuenta.current_password, usuario_actual["account"]["hashed_password"]
        )
        if not contrasenia_valida:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contrasenia actual incorrecta",
            )
        actualizaciones["password"] = datos_cuenta.password

    # Cambio de email
    if datos_cuenta.email and datos_cuenta.email != usuario_actual["account"]["email"]:
        existente = await buscar_por_email(str(datos_cuenta.email))
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya esta registrado por otro usuario",
            )
        actualizaciones["email"] = str(datos_cuenta.email)

    # Cambio de nombre de usuario
    if datos_cuenta.username and datos_cuenta.username != usuario_actual["account"]["username"]:
        existente = await buscar_por_usuario(datos_cuenta.username)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya esta en uso",
            )
        actualizaciones["username"] = datos_cuenta.username

    if datos_cuenta.avatar_url is not None:
        actualizaciones["avatar_url"] = datos_cuenta.avatar_url

    usuario_actualizado = await actualizar_cuenta(id_usuario_actual, actualizaciones)
    if not usuario_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return RespuestaUsuario(
        id=usuario_actualizado["_id"],
        account=RespuestaCuenta(
            username=usuario_actualizado["account"]["username"],
            email=usuario_actualizado["account"]["email"],
            avatar_url=usuario_actualizado["account"]["avatar_url"],
            is_active=usuario_actualizado["account"]["is_active"],
            rol=usuario_actualizado["account"]["rol"],
        ),
        favorites=Favoritos(
            teams=usuario_actualizado["favorites"]["teams"],
            players=usuario_actualizado["favorites"]["players"],
        ),
    )
