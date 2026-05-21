# Importaciones
from pydantic import BaseModel, Field
from typing import List


# Equipos y jugadores favoritos del usuario
class Favoritos(BaseModel):
    teams: List[int] = []
    players: List[int] = []


# Campos comunes a todas las operaciones de cuenta
class CuentaBase(BaseModel):
    username: str
    email: str


# Datos necesarios para crear una cuenta nueva
# password tiene longitud minima de 6 caracteres
class CrearCuenta(CuentaBase):
    password: str = Field(min_length=6)


# Datos de cuenta que se devuelven en las respuestas
class RespuestaCuenta(CuentaBase):
    avatar_url: str = "https://images.icon-icons.com/3446/PNG/512/profile_user_avatar_people_icon_219228.png"
    is_active: bool = True
    rol: str = "user"


# Credenciales para iniciar sesion
class IniciarSesion(BaseModel):
    email: str
    password: str


# Estructura para crear un usuario completo 
class CrearUsuario(BaseModel):
    account: CrearCuenta


# Usuario completo con id, cuenta y favoritos
class RespuestaUsuario(BaseModel):
    id: str
    account: RespuestaCuenta
    favorites: Favoritos


# Respuesta del login: token JWT + datos del usuario
class RespuestaToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: RespuestaUsuario


# Campos que se pueden actualizar del perfil
# Todos son opcionales: solo se envian los que cambian
class ActualizarCuenta(BaseModel):
    email: str | None = None
    username: str | None = None
    avatar_url: str | None = None
    password: str | None = None
    current_password: str | None = None
