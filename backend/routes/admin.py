# Panel de administracion: gestion de usuarios (solo admin)
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from dependencies.auth import obtener_usuario_actual
from config.config import db

router = APIRouter(prefix="/api/admin", tags=["admin"])


# Middleware: solo usuarios con rol admin pueden acceder
async def requerir_admin(usuario_actual: dict = Depends(obtener_usuario_actual)) -> dict:
    if usuario_actual.get("account", {}).get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return usuario_actual


# Lista todos los usuarios (sin la contraseña)
@router.get("/usuarios")
async def listar_usuarios(admin: dict = Depends(requerir_admin)):
    usuarios = []
    cursor = db.users.find({}, {"account.hashed_password": 0})
    async for usuario in cursor:
        usuario["_id"] = str(usuario["_id"])
        usuarios.append(usuario)
    return usuarios


# Activa o desactiva una cuenta
@router.put("/usuarios/{id_usuario}/toggle")
async def toggle_usuario(id_usuario: str, admin: dict = Depends(requerir_admin)):
    usuario = await db.users.find_one({"_id": ObjectId(id_usuario)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # No puedes desactivarte a ti mismo
    if str(usuario["_id"]) == str(admin["_id"]):
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

    nuevo_estado = not usuario["account"]["is_active"]
    await db.users.update_one(
        {"_id": ObjectId(id_usuario)}, {"$set": {"account.is_active": nuevo_estado}}
    )
    return {"mensaje": "Usuario activado" if nuevo_estado else "Usuario desactivado", "id_usuario": id_usuario}


# Borra un usuario
@router.delete("/usuarios/{id_usuario}")
async def borrar_usuario(id_usuario: str, admin: dict = Depends(requerir_admin)):
    if id_usuario == str(admin["_id"]):
        raise HTTPException(status_code=400, detail="No puedes borrar tu propia cuenta")

    resultado = await db.users.delete_one({"_id": ObjectId(id_usuario)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"mensaje": "Usuario eliminado"}
