---
description: "Task list for Solicitudes de Envío"
---

# Tasks: Solicitudes de Envío

**Input**: Design documents from `specs/002-shipments/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | contracts/shipments-api.md ✅ | research.md ✅

**Tests**: No test tasks incluidos (no solicitados en la spec).

**Organization**: Tareas agrupadas por fase. Backend en Foundational (prerequisito del frontend).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias bloqueantes)
- **[Story]**: User story a la que pertenece (US5–US7)
- Paths exactos incluidos en cada descripción

---

## Phase 1: Foundational (Backend Infrastructure)

**Purpose**: Infraestructura backend completa que bloquea todas las user stories del frontend.

**⚠️ CRITICAL**: Ninguna user story de frontend puede completarse hasta que esta fase esté lista.

- [ ] T001 [P] Create `backend/app/schemas/shipment.py` with Pydantic models: `ShipmentCreateRequest` (client_id int, origin str, destination str, cargo_type str, weight_kg float >0, request_date date), `ShipmentCancelRequest` (client_id int), `ShipmentResponse` (request_id int, origin str, destination str, cargo_type str, weight_kg float, request_date date, status str) — validadores: weight_kg > 0, origin/destination/cargo_type not empty
- [ ] T002 [P] Create `backend/app/repositories/shipment_repository.py` with three functions: `create_shipment(client_id, origin, destination, cargo_type, weight_kg, request_date) -> int` (INSERT into fact_shipment_request, status='Pendiente', returns new request_id using `COALESCE(MAX(request_id),0)+1`), `get_shipments_by_client(client_id: int) -> list[dict]` (SELECT all columns WHERE client_id=?), `get_shipment_by_id(request_id: int) -> dict | None` (SELECT WHERE request_id=?), `cancel_shipment(request_id: int)` (UPDATE status='Cancelado' WHERE request_id=?) — all use `from app.core.database import conn`
- [ ] T003 Create `backend/app/services/shipment_service.py` with: `create_shipment_request(client_id, origin, destination, cargo_type, weight_kg, request_date) -> int` (validates origin≠destination, request_date not in past, calls repository), `get_my_shipments(client_id: int) -> list[dict]` (calls repository), `cancel_shipment_request(request_id: int, client_id: int)` (calls get_shipment_by_id, raises HTTPException 404 if not found, 403 if client_id doesn't match, 409 if status≠'Pendiente', then calls cancel_shipment)
- [ ] T004 Create `backend/app/routers/shipments.py` (new `routers/` directory) with FastAPI `APIRouter`: `POST /` (calls create_shipment_request, returns `{"message": "Solicitud de envío creada exitosamente", "request_id": id}` status 201), `GET /my` (extracts client_id from request body or query param — see note below, calls get_my_shipments, returns `{"data": [ShipmentResponse, ...]}`), `PUT /{id}/cancel` (calls cancel_shipment_request with path id and body client_id, returns `{"message": "Solicitud cancelada exitosamente"}`)
- [ ] T005 Update `backend/app/main.py`: add `from app.routers.shipments import router as shipments_router` and `app.include_router(shipments_router, prefix="/shipments", tags=["Shipments"])`

**Checkpoint**: 
```bash
curl -X POST http://localhost:8000/shipments/ \
  -H "Content-Type: application/json" \
  -d '{"client_id":1,"origin":"BOG","destination":"MIA","cargo_type":"General","weight_kg":100,"request_date":"2026-08-01"}'
# → {"message":"Solicitud de envío creada exitosamente","request_id":1}

curl http://localhost:8000/shipments/my
# → {"data":[{...}]}

curl -X PUT http://localhost:8000/shipments/1/cancel \
  -H "Content-Type: application/json" -d '{"client_id":1}'
# → {"message":"Solicitud cancelada exitosamente"}
```

---

## Phase 2: User Story 5 — Crear solicitud de envío (Priority: P1) 🎯 MVP

**Goal**: Cliente autenticado puede crear una nueva solicitud desde la interfaz.

**Independent Test**: Abrir `/shipments`, completar el formulario, hacer clic en "Crear
solicitud" y ver la nueva fila en la lista con estado "Pendiente".

### Implementation for User Story 5

- [ ] T006 [US5] Create `frontend/pages/shipments.py` with `@ui.page('/shipments')`: verify auth with `check_auth()` (redirect to `/login` if False), read user with `get_current_user()`, render form with `ui.input` for origin and destination, `ui.select` or `ui.input` for cargo_type, `ui.number` for weight_kg, `ui.date` for request_date, and `ui.button('Crear solicitud')` that POSTs to `http://backend:8000/shipments/` with `client_id=user['user_id']`; on 201 show `ui.notify('Solicitud creada', color='positive')` and refresh list; on error show `ui.notify(error_detail, color='negative')`
- [ ] T007 [US5] Add `import pages.shipments` at the top of `frontend/app.py` (after existing page imports) so the `/shipments` route gets registered when the app starts

**Checkpoint**: Abrir `http://localhost:8080/shipments` → formulario visible → crear solicitud → aparece en lista con estado "Pendiente"

---

## Phase 3: User Story 6 — Consultar mis solicitudes (Priority: P1)

**Goal**: Cliente puede ver el listado de sus propias solicitudes con todos sus campos.

**Independent Test**: Lista muestra solicitudes del cliente. No muestra solicitudes de otros.
Lista vacía muestra mensaje informativo.

### Implementation for User Story 6

- [ ] T008 [US6] In `frontend/pages/shipments.py` add the shipments list section below the form: call `GET http://backend:8000/shipments/my` (passing client_id via query param or body as documented in contracts), render a `ui.table` with columns request_id, origin, destination, cargo_type, weight_kg, request_date, status and an "actions" column; if the list is empty show `ui.label('No tienes solicitudes de envío registradas.')` with a soft color

**Checkpoint**: Cliente con solicitudes → lista muestra sus filas. Cliente sin solicitudes → mensaje vacío.

---

## Phase 4: User Story 7 — Cancelar una solicitud pendiente (Priority: P2)

**Goal**: Botón "Cancelar" aparece únicamente en filas con estado "Pendiente".
Al cancelar, el estado cambia y el botón desaparece.

**Independent Test**: Fila "Pendiente" → botón visible. Fila "Cancelado" → botón ausente.
Clic en "Cancelar" → estado cambia a "Cancelado" y la fila se actualiza.

### Implementation for User Story 7

- [ ] T009 [US7] In `frontend/pages/shipments.py` add a slot `body-cell-actions` to the shipments table: render a "Cancelar" button only when `props.row.status === 'Pendiente'` (use Quasar's `v-if`); on click emit a `cancel` event with the `request_id`; handle the event with a Python function that calls `PUT http://backend:8000/shipments/{id}/cancel` with `{"client_id": user['user_id']}`, shows `ui.notify` on success or error, and refreshes the table

**Checkpoint**: Fila "Pendiente" → botón "Cancelar" visible. Clic → estado "Cancelado" → botón desaparece. Fila "Cancelado" → botón ausente desde el principio.

---

## Phase 5: Sidebar Integration

**Purpose**: Hacer accesible el módulo desde el sidebar para el rol `cliente`.

- [ ] T010 [P] In `frontend/app.py` add sidebar button for role `cliente`: inside `main_page()`, after the existing visibility assignments, add `_b_ship = ui.button('📦 Mis Envíos', on_click=lambda: ui.navigate.to('/shipments')).classes('sidebar-btn')` and set `_b_ship.visible = rol == 'cliente'`

**Checkpoint**: Login como cliente → sidebar muestra botón "Mis Envíos". Login como administrador o analista → botón no visible.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: Sin dependencias externas a esta feature — empezar aquí
- **US5 (Phase 2)**: Depende de Phase 1 (backend listo) — crea el archivo `shipments.py`
- **US6 (Phase 3)**: Depende de Phase 2 (el archivo `shipments.py` ya existe)
- **US7 (Phase 4)**: Depende de Phase 3 (la tabla ya está renderizada)
- **Sidebar (Phase 5)**: Depende de Phase 2 (la página `/shipments` debe existir)

### Within Each Phase

- T001 y T002 paralelos (archivos distintos)
- T003 depende de T002 (importa funciones del repository)
- T004 depende de T001 y T003 (importa schemas y service)
- T005 depende de T004 (importa el router)
- T006 depende de T005 (backend debe estar listo)
- T007 depende de T006 (el archivo debe existir para importarlo)
- T008 depende de T006 (se añade dentro del mismo archivo)
- T009 depende de T008 (necesita la tabla renderizada)
- T010 puede hacerse en paralelo con T007 (archivo distinto)

### Parallel Opportunities (within Foundational phase)

```bash
# Lanzar en paralelo:
Task: "T001 — Create backend/app/schemas/shipment.py"
Task: "T002 — Create backend/app/repositories/shipment_repository.py"
# Luego:
Task: "T003 — Create backend/app/services/shipment_service.py"
# Luego en paralelo:
Task: "T004 — Create backend/app/routers/shipments.py"
Task: "T005 — Update backend/app/main.py"
```

---

## Implementation Strategy

### MVP First (US5 + US6 — ambas P1)

1. Phase 1: Foundational — backend completo (T001–T005) ← CRITICAL
2. Phase 2: Formulario de creación en frontend (T006–T007)
3. Phase 3: Lista de solicitudes (T008)
4. **STOP y VALIDATE**: quickstart.md escenarios 1 y 2
5. Phase 4: Botón cancelar (T009)
6. **STOP y VALIDATE**: quickstart.md escenarios 3, 4, 6 y 7
7. Phase 5: Sidebar integration (T010)
8. **STOP y VALIDATE**: quickstart.md escenario 5 (acceso sin auth)

### Incremental Delivery

- Backend listo → permite testing con curl antes de tocar el frontend
- Formulario → cliente puede crear solicitudes
- Lista → cliente puede ver sus solicitudes
- Botón cancelar → flujo completo de la US7
- Sidebar → navegación integrada

---

## Notes

- `[P]` = archivos distintos, sin dependencias bloqueantes — pueden ejecutarse en paralelo
- `fact_shipment_request` ya existe; no ejecutar DDL de ningún tipo
- El directorio `backend/app/routers/` es nuevo — crearlo al escribir `shipments.py`
- `frontend/pages/` ya existe — no necesita crearse
- `GET /shipments/my` no tiene request body; el client_id se pasa por query param o se
  lee en el servicio; resolver el mecanismo exacto al implementar T004
- El `client_id` siempre debe extraerse de `app.storage.user['user_id']` en el frontend
  y validarse en el servicio del backend; nunca confiar en el valor sin verificación
