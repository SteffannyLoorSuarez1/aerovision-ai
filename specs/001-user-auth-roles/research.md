# Research: Autenticación y Gestión de Usuarios

**Feature**: 001-user-auth-roles
**Date**: 2026-06-24

---

## 1. NiceGUI Session Management

**Decision**: Usar `app.storage.user` de NiceGUI como mecanismo de sesión.

**Rationale**:
- `app.storage.user` es un dict persistente por conexión de navegador (sobrevive recargas
  de página) que NiceGUI cifra con el `storage_secret` configurado en `ui.run()`.
- No requiere cookies manuales ni JWT.
- Accesible desde cualquier función de página sin pasar argumentos.
- La sesión se invalida al cerrar el navegador o al borrar el storage explícitamente.

**Pattern**:
```python
# Verificar autenticación al inicio de cada página protegida
if not app.storage.user.get('authenticated', False):
    ui.navigate.to('/login')
    return
```

**Alternatives considered**:
- `app.storage.client` (por-conexión, no persiste al recargar) → descartado: el usuario
  perdería la sesión al recargar.
- JWT + cookies manuales → descartado: la constitución lo prohíbe explícitamente.
- Sesión en DuckDB → descartado: innecesaria complejidad para una sesión local.

---

## 2. bcrypt en Python

**Decision**: Usar la librería `bcrypt` directamente (ya en el stack).

**Pattern**:
```python
import bcrypt
# Hash al registrar:
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
# Verificar al login:
bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
```

**Rationale**: bcrypt incluye salt automáticamente y es resistente a ataques de fuerza
bruta por su costo computacional configurable. La constitución lo especifica explícitamente.

**Alternatives considered**:
- `passlib` (wrapper de bcrypt) → descartado: dependencia adicional innecesaria.
- SHA-256 → descartado: no apto para contraseñas (rápido, sin salt nativo).

---

## 3. Arquitectura de páginas en NiceGUI

**Decision**: Crear páginas de login y registro como archivos separados con decorador
`@ui.page('/login')` y `@ui.page('/register')`. La página principal usa `@ui.page('/')`.

**Rationale**:
- La constitución (Regla 1) exige código nuevo en archivos separados.
- `frontend/app.py` ya tiene 2400+ líneas; añadir auth inline agravaría el problema.
- `@ui.page()` es el patrón nativo de NiceGUI para multi-página.

**Pattern**:
```python
# frontend/pages/login.py
from nicegui import ui, app as nicegui_app

@ui.page('/login')
def login_page():
    # Si ya está autenticado, redirigir al inicio
    if nicegui_app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return
    # Renderizar formulario de login...
```

**Alternatives considered**:
- Incrustarlo todo en `app.py` → descartado: viola constitución y empeora la deuda técnica.
- Usar `ui.navigate.to()` con show/hide en la misma página → descartado: no aísla la lógica
  de auth del contenido.

---

## 4. Backend: Endpoint de autenticación

**Decision**: Crear un nuevo router `backend/app/api/users.py` con endpoints `POST /users/register`
y `POST /users/login`. La validación de credenciales ocurre en el backend; el frontend gestiona
el estado de sesión localmente via NiceGUI storage.

**Rationale**:
- Sigue el patrón Repository → Service → API ya establecido en el codebase.
- El backend actúa como validador stateless; el estado de sesión vive en el frontend.
- No se emiten tokens ni cookies desde el backend.

**Alternatives considered**:
- Autenticación completamente en el frontend (DuckDB desde frontend) → descartado: la
  constitución lo prohíbe (Principio III, Frontend–Backend Contract).
- Sessions en el backend con cookies → descartado: viola la restricción de "sin JWT,
  sesión manejada por NiceGUI nativo".

---

## 5. DuckDB: Creación de dim_users

**Decision**: Crear `dim_users` con tipos correctos y SEQUENCE para el ID, usando
`CREATE TABLE IF NOT EXISTS` en `init_warehouse.py` o en un script de migración separado.

**Rationale**:
- La constitución especifica que tablas nuevas usan `INTEGER`, `FLOAT`, `TIMESTAMP`,
  nunca `VARCHAR` para métricas.
- Se usa SEQUENCE para IDs incrementales en lugar de `MAX(id)+1` para evitar race conditions.
- No se modifica ninguna tabla existente (dim_airline, dim_airport, etc.).

**Schema decidido**:
```sql
CREATE SEQUENCE IF NOT EXISTS users_id_seq START 1;
CREATE TABLE IF NOT EXISTS dim_users (
    id          INTEGER DEFAULT nextval('users_id_seq') PRIMARY KEY,
    nombre      VARCHAR NOT NULL,
    email       VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    rol         VARCHAR NOT NULL DEFAULT 'cliente',
    fecha_creacion TIMESTAMP DEFAULT current_timestamp,
    activo      BOOLEAN DEFAULT true
);
```

**Alternatives considered**:
- `AUTOINCREMENT` → DuckDB usa `SEQUENCE` en su lugar.
- Añadir columna `rol` a tabla existente → descartado: no se modifica ninguna tabla existente.

---

## 6. Control de acceso por rol en el sidebar

**Decision**: El sidebar de `frontend/app.py` se hace dinámico: lee el rol del usuario
desde `app.storage.user` y muestra solo los botones correspondientes. La inicialización
de la app se envuelve en `@ui.page('/')` con verificación de auth.

**Rol → módulos permitidos**:

| Rol           | Módulos visibles                                                    |
|---------------|---------------------------------------------------------------------|
| cliente       | (módulos de negocio — cotización, reservas, etc. — fase 2)         |
| administrador | Dashboard, Warehouse, CRUD (4), Flight Map, Operations, Import      |
| analista      | Dashboard, Flight Map, Operations Center                            |

**Note**: Los módulos de cliente (cotización, reservas) aún no existen en el frontend;
el cliente verá una vista de bienvenida por ahora.

---

## Resumen de decisiones clave

| Tema                     | Decisión                                  |
|--------------------------|-------------------------------------------|
| Sesión                   | `app.storage.user` de NiceGUI             |
| Hash de contraseñas      | `bcrypt` directamente                     |
| Páginas auth             | Archivos separados con `@ui.page()`       |
| Backend auth             | Router `/users` con register + login      |
| BD usuarios              | `dim_users` nueva tabla en DuckDB         |
| Control de acceso        | Sidebar dinámico por rol                  |
