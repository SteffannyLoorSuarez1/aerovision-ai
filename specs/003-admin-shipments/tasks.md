---
description: "Task list for Panel de Envíos para Admin/Analista"
---

# Tasks: Panel de Envíos para Admin/Analista

**Input**: Design documents from `specs/003-admin-shipments/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | contracts/admin-shipments-api.md ✅ | research.md ✅

**Tests**: No test tasks incluidos (no solicitados en la spec).

**Organization**: Tareas agrupadas por fase. Backend primero (prerequisito del frontend).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias bloqueantes)
- **[Story]**: User story a la que pertenece (US8–US9)
- Paths exactos incluidos en cada descripción

---

## Phase 1: Backend

**Purpose**: Exponer el endpoint `GET /shipments/all` con JOIN a `dim_users`.

**⚠️ CRITICAL**: El frontend no puede completarse hasta que esta fase esté lista.

- [ ] T001 [US8] In `backend/app/schemas/shipment.py` add `AdminShipmentResponse` model: `request_id int`, `client_id int`, `client_name str`, `client_email str`, `origin str`, `destination str`, `cargo_type str`, `weight_kg float`, `request_date date`, `status str`, `created_at str` — add after existing models, no other changes

- [ ] T002 [US8] In `backend/app/repositories/shipment_repository.py` add function `get_all_shipments(status: str | None = None) -> list[dict]`: execute LEFT JOIN query between `fact_shipment_request` and `dim_users` using `COALESCE(u.nombre, '[Usuario eliminado]') AS client_name` and `COALESCE(u.email, '[sin email]') AS client_email`; if `status` is not None add `WHERE s.status = ?`; order by `s.request_id DESC`; return list of dicts with all columns

- [ ] T003 [US8] In `backend/app/services/shipment_service.py` add function `get_all_shipments_service(status: str | None = None) -> list[dict]`: call `get_all_shipments(status)` from repository and return result — no additional business logic needed in this delivery

- [ ] T004 [US8] In `backend/app/routers/shipments.py` add endpoint `GET /all`: accepts optional query parameter `status: str | None = Query(None)`, calls `get_all_shipments_service(status)`, returns `{"data": result}` with status 200

**Checkpoint Phase 1**:
```bash
# All shipments
curl http://localhost:8000/shipments/all
# → {"data": [{request_id, client_id, client_name, client_email, origin, destination, cargo_type, weight_kg, request_date, status, created_at}]}

# Filter by status
curl "http://localhost:8000/shipments/all?status=Pendiente"
# → {"data": [{...only Pendiente...}]}

# Empty table
curl http://localhost:8000/shipments/all
# → {"data": []}
```

---

## Phase 2: Frontend

**Purpose**: Panel visible en sidebar para admin/analista con tabla y filtro de estado.

- [ ] T005 [US8] [US9] In `frontend/app.py` add function `show_admin_shipments()` before `# MAIN PAGE` comment: call `content.clear()`, render `ui.label('📋 Gestión de Envíos').classes('title')` and `ui.separator()`, make a `requests.get(f'{API_URL}/shipments/all', timeout=10)` call, store result in `all_data`, render filter selector `ui.select(['Todas', 'Pendiente', 'Cancelado'], value='Todas')` and a `ui.table` with columns `request_id, client_name, client_email, origin, destination, cargo_type, weight_kg, request_date, status`; when filter changes update `table.rows` filtering `all_data` by status; if list empty show `ui.label('No hay solicitudes de envío registradas.')` with soft color; on connection error show `ui.notify(..., color='negative')`

- [ ] T006 [US8] In `frontend/app.py` inside `main_page()`: add `_b_admin_ship = ui.button('📋 Gestión de Envíos', on_click=show_admin_shipments).classes('sidebar-btn')` after `_b_ship` button; add `_b_admin_ship.visible = rol in ('administrador', 'analista')` in the visibility block after `_b_ship.visible = rol == 'cliente'`

**Checkpoint Phase 2**:
```
1. Login como admin → sidebar muestra "📋 Gestión de Envíos"
2. Login como analista → sidebar muestra "📋 Gestión de Envíos"
3. Login como cliente → botón NO aparece en sidebar
4. Admin abre panel → tabla muestra todas las solicitudes con columna "Cliente"
5. Selector "Pendiente" → solo filas con status Pendiente
6. Selector "Todas" → todas las filas
7. Sin solicitudes → mensaje informativo
```

---

## Dependencies & Execution Order

- T001 y T002 pueden ejecutarse en paralelo (archivos distintos)
- T003 depende de T002 (importa `get_all_shipments`)
- T004 depende de T001 y T003 (importa schema y service)
- T005 y T006 dependen de T004 (backend debe estar listo)
- T005 antes que T006 (la función debe existir para referenciarla en el botón)

---

## Notes

- No crear nuevos archivos. Todos los cambios son adiciones a archivos existentes.
- No modificar endpoints existentes de SPEC-002 (`POST /`, `GET /my`, `PUT /{id}/cancel`).
- El filtrado por estado en T005 ocurre en el frontend: `table.rows = [r for r in all_data if r['status'] == selected]` o `all_data` completo si se selecciona "Todas".
- `created_at` se almacena como VARCHAR (CAST en SQL) para evitar problemas de serialización de timestamp de DuckDB.
- Las acciones sobre solicitudes (aprobar, rechazar, cambiar estado) se implementan en SPEC-007; en esta entrega el panel es estrictamente de solo lectura para ambos roles.
