# Implementation Plan: Autenticación y Gestión de Usuarios

**Branch**: `001-user-auth-roles` | **Date**: 2026-06-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-user-auth-roles/spec.md`

---

## Summary

Implementar el sistema de autenticación de AeroVision AirCargo Exchange: registro de
usuarios (rol cliente por defecto), login con verificación bcrypt, sesión nativa de
NiceGUI por `app.storage.user`, y control de acceso por rol (cliente / administrador /
analista) que filtra dinámicamente el sidebar y bloquea módulos no permitidos.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI (backend), NiceGUI (frontend), DuckDB (almacenamiento),
bcrypt (hashing de contraseñas), Pydantic v2 (validación)

**Storage**: DuckDB — nueva tabla `dim_users` con tipos correctos (INTEGER, VARCHAR,
BOOLEAN, TIMESTAMP). No se modifica ninguna tabla existente.

**Testing**: Validación manual vía quickstart.md (no se requieren tests automatizados
en esta entrega)

**Target Platform**: Linux container vía Docker Compose

**Project Type**: Web application (backend FastAPI + frontend NiceGUI)

**Performance Goals**: Login y registro responden en < 2 segundos. bcrypt factor de
costo estándar (12 rondas).

**Constraints**: Sin JWT. Sin cookies manuales. Sesión manejada por `app.storage.user`
de NiceGUI. Contraseñas almacenadas solo como hash bcrypt irreversible.

**Scale/Scope**: Single-tenant, decenas de usuarios concurrentes.

---

## Constitution Check

*GATE: Verificación pre-implementación contra los 5 principios.*

| Principio                      | Estado | Notas                                                                     |
|--------------------------------|--------|---------------------------------------------------------------------------|
| I. Data-First Analytics        | ✅     | `dim_users` usa tipos correctos. Tablas existentes intactas.              |
| II. Clean Layered Backend      | ✅     | Repository → Service → Router. Sin SQL en endpoints ni lógica en repositorio. |
| III. Frontend–Backend Contract | ✅     | Frontend solo llama a `/users/register` y `/users/login`. Sin DuckDB directo. |
| IV. Containerized Portability  | ✅     | `storage_secret` via env var. Sin hardcoding de credenciales.             |
| V. Simplicity & YAGNI          | ✅     | Sin JWT, sin refresh tokens, sin middleware complejo. Mínima complejidad. |

**Resultado**: PASS — sin violaciones. Puede proceder a implementación.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-user-auth-roles/
├── plan.md              # Este archivo
├── research.md          # Decisiones técnicas y alternativas evaluadas
├── data-model.md        # Schema de dim_users y reglas de validación
├── quickstart.md        # Guía de validación end-to-end
├── contracts/
│   └── users-api.md     # Contratos POST /users/register y POST /users/login
└── tasks.md             # Generado por /speckit-tasks
```

### Source Code

```text
backend/
├── app/
│   ├── api/
│   │   └── users.py           # NUEVO: Router /users (register + login)
│   ├── repositories/
│   │   └── user_repository.py # NUEVO: Queries DuckDB para dim_users
│   ├── schemas/
│   │   └── user.py            # NUEVO: UserRegisterRequest, UserLoginRequest, UserResponse
│   ├── services/
│   │   └── user_service.py    # NUEVO: Lógica de negocio (hash, validaciones)
│   ├── core/
│   │   └── init_warehouse.py  # MODIFICAR: Añadir CREATE TABLE dim_users al startup
│   └── main.py                # MODIFICAR: include_router(users_router)

frontend/
├── app.py                     # MODIFICAR: @ui.page('/'), auth guard, sidebar dinámico
├── auth.py                    # NUEVO: check_auth(), get_current_user(), logout()
└── pages/
    ├── login.py               # NUEVO: @ui.page('/login') — formulario de login
    └── register.py            # NUEVO: @ui.page('/register') — formulario de registro
```

**Structure Decision**: Web application. Backend y frontend ya existentes. Archivos nuevos
por módulo; `frontend/app.py` se modifica solo lo mínimo para envolver el contenido en
`@ui.page('/')` y hacer el sidebar dinámico.

---

## Phase 0: Research

**Status**: COMPLETE — ver [research.md](research.md)

Decisiones resueltas:
- Sesión: `app.storage.user` de NiceGUI (no JWT, no cookies)
- Hash: `bcrypt` directamente (no passlib)
- Páginas: archivos separados con `@ui.page()`
- Backend auth: Router stateless en `/users`
- BD: nueva tabla `dim_users` con SEQUENCE para IDs

---

## Phase 1: Design & Contracts

**Status**: COMPLETE

Artefactos generados:
- [data-model.md](data-model.md) — Schema SQL de `dim_users`, reglas de validación,
  relaciones futuras
- [contracts/users-api.md](contracts/users-api.md) — Contratos POST /users/register y
  POST /users/login con schemas Pydantic completos
- [quickstart.md](quickstart.md) — 6 escenarios de validación end-to-end con curls

---

## Phase 2: Implementation

Ver [tasks.md](tasks.md) (generado por `/speckit-tasks`).

**Orden de construcción**:

1. **Backend primero** (prerequisito para el frontend):
   - `dim_users` en DuckDB (init_warehouse.py)
   - `user_repository.py` — queries CRUD básico
   - `user_service.py` — hashing bcrypt + validaciones de negocio
   - `schemas/user.py` — Pydantic models
   - `api/users.py` — endpoints register/login
   - `main.py` — include_router(users_router)

2. **Frontend segundo**:
   - `frontend/auth.py` — helpers de sesión (check_auth, logout)
   - `frontend/pages/login.py` — página de login
   - `frontend/pages/register.py` — página de registro
   - `frontend/app.py` — auth guard + sidebar dinámico por rol

**Checkpoints de validación**:
1. `curl POST /users/register` crea usuario con hash en DuckDB
2. `curl POST /users/login` devuelve datos del usuario
3. `/register` y `/login` funcionan en el navegador
4. Sidebar muestra módulos correctos según rol autenticado
5. Cierre de sesión redirige al login y bloquea acceso directo

---

## Complexity Tracking

*No hay violaciones a la constitución que justificar.*
