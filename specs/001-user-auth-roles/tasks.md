---
description: "Task list for Autenticación y Gestión de Usuarios"
---

# Tasks: Autenticación y Gestión de Usuarios

**Input**: Design documents from `specs/001-user-auth-roles/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | contracts/users-api.md ✅ | research.md ✅

**Tests**: No test tasks incluidos (no solicitados en la spec).

**Organization**: Tareas agrupadas por user story. Backend en Foundational (sirve US1 y US2).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias bloqueantes)
- **[Story]**: User story a la que pertenece (US1–US4)
- Paths exactos incluidos en cada descripción

---

## Phase 1: Setup

**Purpose**: Preparar dependencias del proyecto

- [ ] T001 Add `bcrypt` and `email-validator` to backend/requirements.txt (needed for password hashing and Pydantic EmailStr validation)

**Checkpoint**: `pip install -r backend/requirements.txt` sin errores

---

## Phase 2: Foundational (Backend Infrastructure)

**Purpose**: Infraestructura backend compartida que bloquea todas las user stories

**⚠️ CRITICAL**: Ninguna user story puede completarse hasta que esta fase esté lista

- [ ] T002 [P] Create backend/app/schemas/user.py with Pydantic models: `UserRegisterRequest` (nombre str, email EmailStr, password str min_length=8), `UserLoginRequest` (email EmailStr, password str), `UserResponse` (id int, nombre str, email str, rol str)
- [ ] T003 [P] Create backend/app/repositories/user_repository.py with two functions: `find_by_email(email: str) -> dict | None` and `create_user(nombre: str, email: str, password_hash: str) -> int` — both use `from app.core.database import conn`; `create_user` uses `SELECT nextval('users_id_seq')` for the id
- [ ] T004 Create backend/app/services/user_service.py with `register_user(nombre, email, password)` (validates email uniqueness, hashes with `bcrypt.hashpw`, calls `create_user`, raises `HTTPException(400)` if email exists) and `authenticate_user(email, password)` (calls `find_by_email`, raises `HTTPException(401)` if not found, `HTTPException(403)` if `activo=False`, verifies hash with `bcrypt.checkpw`)
- [ ] T005 Create backend/app/api/users.py with FastAPI `APIRouter`, `POST /register` endpoint (calls `register_user`, returns `{"message": "Usuario registrado exitosamente", "user_id": id}` with status 201) and `POST /login` endpoint (calls `authenticate_user`, returns `UserResponse`)
- [ ] T006 Update backend/app/main.py: add `@app.on_event("startup")` handler that creates `SEQUENCE IF NOT EXISTS users_id_seq` and `TABLE IF NOT EXISTS dim_users` (schema from data-model.md); then add `app.include_router(users_router, prefix="/users", tags=["Users"])`

**Checkpoint**: `curl -X POST http://localhost:8000/users/register -H "Content-Type: application/json" -d '{"nombre":"Test","email":"test@x.com","password":"pass1234"}'` returns `{"message":"Usuario registrado exitosamente","user_id":1}` and `curl POST /users/login` returns `{"id":1,"nombre":"Test","email":"test@x.com","rol":"cliente"}`

---

## Phase 3: User Story 1 — Registro de nuevo usuario (Priority: P1) 🎯 MVP

**Goal**: Cualquier visitante puede registrarse en la plataforma con nombre, email y contraseña.

**Independent Test**: Navegar a `http://localhost:8080/register`, completar el formulario, y recibir confirmación con redirección a `/login`. La cuenta aparece en `dim_users`.

### Implementation for User Story 1

- [ ] T007 [US1] Create frontend/pages/register.py with `@ui.page('/register')` function: dark-themed card (matching existing `main-card` CSS class) with `ui.input` fields for nombre, email, password (type='password'), a "Registrarse" button that POSTs to `http://backend:8000/users/register`, shows `ui.notify` on error, and calls `ui.navigate.to('/login')` on 201 success; if already authenticated (`app.storage.user.get('authenticated')`), redirect immediately to '/'
- [ ] T008 [US1] Add `import frontend.pages.register` at the top of frontend/app.py (after existing imports) so the `/register` route gets registered when the app starts

**Checkpoint**: Abrir `http://localhost:8080/register` → formulario visible → registro exitoso → redirige a `/login`

---

## Phase 4: User Story 2 — Inicio de sesión con redirección por rol (Priority: P1)

**Goal**: Usuario registrado inicia sesión y el sistema lo redirige automáticamente a su vista de rol.

**Independent Test**: Login con `test@x.com` → `app.storage.user` contiene `{authenticated: True, rol: "cliente", ...}` → redirige a '/'. Login con admin → redirige a '/' con sidebar completo.

### Implementation for User Story 2

- [ ] T009 [P] [US2] Create frontend/auth.py with three functions: `check_auth() -> bool` (returns `app.storage.user.get('authenticated', False)`), `get_current_user() -> dict` (returns `dict(app.storage.user)`), and `logout()` (calls `app.storage.user.clear()` then `ui.navigate.to('/login')`)
- [ ] T010 [US2] Create frontend/pages/login.py with `@ui.page('/login')` function: dark-themed card with `ui.input` for email and `ui.input(password=True)` for password, "Iniciar sesión" button that POSTs to `http://backend:8000/users/login`; on 200 stores `{authenticated: True, user_id, nombre, email, rol}` in `app.storage.user` and calls `ui.navigate.to('/')`, on 401/403 shows `ui.notify` with error message; if already authenticated, redirect to '/'
- [ ] T011 [US2] Add `NICEGUI_STORAGE_SECRET` env var to docker-compose.yml under the frontend service environment section (value: a random string e.g. `aerovision-dev-secret-2026`)
- [ ] T012 [US2] Update frontend/app.py: add `import os` and `import frontend.pages.login` at top; change `ui.run(host='0.0.0.0', port=8080)` to `ui.run(host='0.0.0.0', port=8080, storage_secret=os.environ.get('NICEGUI_STORAGE_SECRET', 'aerovision-dev-secret-2026'))`

**Checkpoint**: Abrir `http://localhost:8080/login` → login con test@x.com → redirige a `/` → `app.storage.user['rol']` es `'cliente'`

---

## Phase 5: User Story 3 — Control de acceso por rol (Priority: P1)

**Goal**: Cada usuario ve solo los módulos de su rol. Acceso directo a módulos no permitidos es bloqueado.

**Independent Test**: Analista autenticado → sidebar solo muestra Dashboard, Flight Map, Operations Center. Cliente → no ve CRUD ni Import. Acceso directo a la app sin login → redirige a `/login`.

### Implementation for User Story 3

- [ ] T013 [US3] Wrap all page content in frontend/app.py inside a `@ui.page('/')` decorated function: move the sidebar `with ui.column().classes('sidebar'):` block and `content = ui.column()...` and `show_dashboard()` call inside this function; add `from frontend.auth import check_auth, get_current_user` at top; at the start of the function add: `if not check_auth(): ui.navigate.to('/login'); return`
- [ ] T014 [US3] Make sidebar dynamic inside the `@ui.page('/')` function in frontend/app.py: call `user = get_current_user()` and `rol = user.get('rol', '')`, then use conditional rendering — `if rol in ('administrador',)` to show CRUD buttons and Import; `if rol in ('administrador', 'analista')` to show Warehouse; always show Dashboard, Flight Map, Operations Center for `administrador` and `analista`; show only a "Bienvenido" message area for `cliente`

**Checkpoint**: Login como analista → sidebar tiene solo 3 botones. Login como administrador → sidebar completo. Sin login → redirige a `/login`.

---

## Phase 6: User Story 4 — Cierre de sesión (Priority: P2)

**Goal**: Usuario puede cerrar sesión desde cualquier pantalla; sesión queda invalidada.

**Independent Test**: Click "Cerrar sesión" → redirige a `/login`. Botón "atrás" del navegador o URL directa → redirige de nuevo a `/login`.

### Implementation for User Story 4

- [ ] T015 [US4] Add "Cerrar sesión" button at the bottom of the sidebar in frontend/app.py: after `ui.space()`, add `ui.button('🚪 Cerrar sesión', on_click=lambda: logout()).classes('sidebar-btn').style('background: linear-gradient(135deg, #dc2626, #ef4444)')` and add `from frontend.auth import logout` to the imports at top of the `@ui.page('/')` function

**Checkpoint**: Click "Cerrar sesión" → redirige a `/login`. Navegar a `http://localhost:8080/` sin login → redirige a `/login`.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Detalles de UX y validación final

- [ ] T016 [P] Add user greeting to sidebar in frontend/app.py: inside the `@ui.page('/')` function, after the logo/subtitle block add `ui.label(f"👤 {user.get('nombre', '')}").style('color:#93c5fd; font-size:14px; margin-top:8px')` and `ui.label(f"Rol: {rol}").style('color:#64748b; font-size:12px')`
- [ ] T017 [P] Add welcome view for role "cliente" in frontend/app.py: create `show_bienvenida(nombre)` function that shows a welcome card with the user's name and a message explaining that cargo booking modules are coming soon; call it as default content for `rol == 'cliente'` instead of `show_dashboard()`
- [ ] T018 Run `docker compose up --build` and validate all 6 scenarios from `specs/001-user-auth-roles/quickstart.md` (registro exitoso, login por rol, bloqueo de acceso, cierre de sesión, validaciones de formulario, login fallido)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — empezar aquí
- **Foundational (Phase 2)**: Depende de Phase 1 (bcrypt instalado) — BLOQUEA todas las US
- **US1 (Phase 3)**: Depende de Foundational — no depende de otras US
- **US2 (Phase 4)**: Depende de Foundational — no depende de US1
- **US3 (Phase 5)**: Depende de US2 (necesita sesión para verificar) y US1 (la página de registro debe ser accesible)
- **US4 (Phase 6)**: Depende de US3 (el sidebar dinámico ya existe)
- **Polish (Phase 7)**: Depende de todas las US completadas

### Within Each Phase

- T002 y T003 paralelos (archivos distintos)
- T004 depende de T003 (importa schemas)
- T005 depende de T002 y T003
- T006 depende de T005
- T009 y T010, T011 paralelos (archivos distintos)
- T012 depende de T011 (env var debe estar definida)
- T013 y T014 en el mismo archivo: T014 depende de T013
- T016 y T017 paralelos (secciones distintas del mismo archivo)

### Parallel Opportunities (within Foundational phase)

```bash
# Lanzar en paralelo:
Task: "T002 — Create backend/app/schemas/user.py"
Task: "T003 — Create backend/app/repositories/user_repository.py"
# Luego:
Task: "T004 — Create backend/app/services/user_service.py"
# Luego:
Task: "T005 — Create backend/app/api/users.py"
Task: "T006 — Update backend/app/main.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 — todas P1)

1. Phase 1: Setup (T001)
2. Phase 2: Foundational — backend completo (T002–T006) ← CRITICAL
3. Phase 3: Registro frontend (T007–T008)
4. Phase 4: Login frontend + sesión (T009–T012)
5. Phase 5: Auth guard + sidebar dinámico (T013–T014)
6. **STOP y VALIDATE**: quickstart.md escenarios 1–3
7. Phase 6: Logout (T015)
8. **STOP y VALIDATE**: quickstart.md escenario 4
9. Phase 7: Polish (T016–T018)

### Incremental Delivery

- Backend ready → permite testing con curl antes de tocar el frontend
- Register page → usuario puede crear cuenta
- Login + sesión → usuario puede autenticarse
- Sidebar dinámico → acceso controlado por rol
- Logout → flujo completo end-to-end

---

## Notes

- `[P]` = archivos distintos, sin dependencias bloqueantes — pueden ejecutarse en paralelo
- `[Story]` mapea cada tarea a su user story para trazabilidad
- `app.storage.user` se comparte entre rerenders de la misma conexión (no entre tabs distintos)
- `init_warehouse.py` solo corre cuando `warehouse.duckdb` no existe; `dim_users` se crea con startup event para garantizar que siempre existe
- El sidebar actual en `frontend/app.py` está al nivel del módulo (fuera de cualquier función); T013 lo mueve dentro de `@ui.page('/')` — es el cambio más delicado
- `frontend/pages/` ya existe (`operations_center.py` está ahí); el directorio no necesita crearse
