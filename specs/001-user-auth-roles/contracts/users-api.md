# API Contracts: Users

**Router prefix**: `/users`
**File**: `backend/app/api/users.py`
**Tags**: `["Users"]`

---

## POST /users/register

Registra un nuevo usuario con rol `cliente`.

### Request

```json
{
  "nombre": "string (1-100 chars, required)",
  "email": "string (valid email format, required)",
  "password": "string (min 8 chars, required)"
}
```

**Pydantic schema**: `UserRegisterRequest` en `backend/app/schemas/user.py`

### Responses

**201 Created** — Registro exitoso:
```json
{
  "message": "Usuario registrado exitosamente",
  "user_id": 1
}
```

**400 Bad Request** — Email ya registrado:
```json
{
  "detail": "El email ya está registrado"
}
```

**422 Unprocessable Entity** — Validación fallida (email inválido, contraseña < 8 chars,
nombre vacío). FastAPI lo genera automáticamente desde el schema Pydantic.

---

## POST /users/login

Verifica credenciales y devuelve los datos del usuario (sin token).

### Request

```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Pydantic schema**: `UserLoginRequest` en `backend/app/schemas/user.py`

### Responses

**200 OK** — Credenciales válidas:
```json
{
  "id": 1,
  "nombre": "Juan García",
  "email": "juan@example.com",
  "rol": "cliente"
}
```

**401 Unauthorized** — Credenciales incorrectas (email no existe o contraseña errónea).
El mensaje es intencionalmente genérico para no revelar cuál campo es el incorrecto:
```json
{
  "detail": "Credenciales inválidas"
}
```

**403 Forbidden** — Cuenta desactivada:
```json
{
  "detail": "Cuenta desactivada"
}
```

---

## Pydantic Schemas (`backend/app/schemas/user.py`)

```python
from pydantic import BaseModel, EmailStr, field_validator

class UserRegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str

    @field_validator('nombre')
    def nombre_not_empty(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

    @field_validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
```

---

## Notas de implementación

- **No se emiten tokens**: el backend solo valida y devuelve datos; el frontend gestiona
  el estado de sesión con `app.storage.user`.
- **Respuesta de login deliberadamente simple**: no incluye `activo` ni `fecha_creacion`
  para minimizar la superficie de datos expuesta al frontend.
- **Error 401 vs 404**: siempre 401 cuando las credenciales fallan, nunca 404 por "email
  no encontrado" (evita user enumeration).
