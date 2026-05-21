# Importaciones
from bson import ObjectId
from passlib.context import CryptContext
from config.config import db

# Configuracion de bcrypt para cifrar y verificar contraseñas
contexto_seguridad = CryptContext(schemes=["bcrypt"])

# Cifra contraseña con bypt y devuelve hash seguro para almacenar en la base de datos
def cifrar_contrasenia(contrasenia: str) -> str:
    return contexto_seguridad.hash(contrasenia)

# Veriica que la contraseña coincide con el hash almacenado en la base de datos
def verificar_contrasenia(contrasenia_plana: str, contrasenia_hasheada: str) -> bool:
    return contexto_seguridad.verify(contrasenia_plana, contrasenia_hasheada)

# Insertar un nuevo usuario en la coleccion users
async def crear_usuario(datos_cuenta: dict) -> dict:
    contrasenia_hasheada = cifrar_contrasenia(datos_cuenta["password"])

    usuario = {
        "account": {
            "username": datos_cuenta["username"],
            "email": datos_cuenta["email"],
            "hashed_password": contrasenia_hasheada,
            "avatar_url": "https://images.icon-icons.com/3446/PNG/512/profile_user_avatar_people_icon_219228.png",
            "is_active": True,
            "rol": "user",
        },
        "favorites": {
            "teams": [],
            "players": [],
        },
    }

    resultado = await db.users.insert_one(usuario)
    # Añade el id generado por MongoDB al diccionario del usuario para devolverlo
    usuario["_id"] = str(resultado.inserted_id)
    return usuario

# Busca un usuario nombre de usuario 
async def buscar_por_usuario(nombre_usuario: str) -> dict | None:
    usuario = await db.users.find_one({"account.username": nombre_usuario})
    if usuario:
        usuario["_id"] = str(usuario["_id"])
    return usuario

# Busca un usuario correo electronico 
async def buscar_por_email(correo: str) -> dict | None:
    usuario = await db.users.find_one({"account.email": correo})
    if usuario:
        usuario["_id"] = str(usuario["_id"])
    return usuario

# Busca un usuario por su id
async def buscar_por_id(id_usuario: str) -> dict | None:
    try:
        usuario = await db.users.find_one({"_id": ObjectId(id_usuario)})
        if usuario:
            usuario["_id"] = str(usuario["_id"])
        return usuario
    except:
        return None

# Actualiza campos de la cuenta del usuario (email, username, avatar, password)
async def actualizar_cuenta(id_usuario: str, cambios: dict) -> dict | None:
    campos = {}

    if "email" in cambios:
        campos["account.email"] = cambios["email"]
    if "username" in cambios:
        campos["account.username"] = cambios["username"]
    if "avatar_url" in cambios:
        campos["account.avatar_url"] = cambios["avatar_url"]
    if "password" in cambios:
        campos["account.hashed_password"] = cifrar_contrasenia(cambios["password"])

    # Si no hay campos que actualizar, devuelve el usuario sin modificar
    if not campos:
        return await buscar_por_id(id_usuario)

    # find_one_and_update con return_document=True devuelve el documento ya actualizado
    resultado = await db.users.find_one_and_update(
        {"_id": ObjectId(id_usuario)}, {"$set": campos}, return_document=True
    )

    if resultado:
        resultado["_id"] = str(resultado["_id"])
    return resultado
