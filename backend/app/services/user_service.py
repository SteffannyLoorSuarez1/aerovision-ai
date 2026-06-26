import bcrypt
from fastapi import HTTPException

from app.repositories.user_repository import find_by_email, create_user


def register_user(nombre: str, email: str, password: str) -> int:
    if find_by_email(email) is not None:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    return create_user(nombre, email, password_hash)


def authenticate_user(email: str, password: str) -> dict:
    user = find_by_email(email)

    if user is None:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not user['activo']:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {
        'id': user['id'],
        'nombre': user['nombre'],
        'email': user['email'],
        'rol': user['rol'],
    }
