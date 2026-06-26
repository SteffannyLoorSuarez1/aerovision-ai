# Implementation Plan: Solicitudes de Envío

**Branch**: `002-shipments` | **Date**: 2026-06-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-shipments/spec.md`

---

## Summary

Implementar el módulo de Solicitudes de Envío de AeroVision AirCargo Exchange: creación
de solicitudes por parte del cliente autenticado, consulta de sus propias solicitudes y
cancelación de solicitudes en estado "Pendiente". La tabla `fact_shipment_request` ya
existe; el módulo opera sobre ella sin modificarla.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI (backend), NiceGUI (frontend), DuckDB (almacenamiento),
Pydantic v2 (validación). Sin nuevas dependencias respecto a SPEC-001.

**Storage**: DuckDB — tabla `fact_shipment_request` existente. No se crea ni modifica
ninguna tabla del warehouse.

**Testing**: Validación manual vía quickstart.md (no se requieren tests automatizados
en esta entrega).

**Target Platform**: Linux container vía Docker Compose

**Project Type**: Web application (backend FastAPI + frontend NiceGUI)

**Performance Goals**: Creación y consulta de solicitudes responden en < 2 segundos.

**Constraints**: Sin JWT. Sin cookies manuales. El `client_id` se extrae siempre de la
sesión (`app.storage.user['user_id']`). La tabla `fact_shipment_request` no se altera.

**Scale/Scope**: Single-tenant, decenas de usuarios concurrentes. Sin paginación en
esta entrega.

**Prerequisito**: SPEC-001 completada — `dim_users` existe y la autenticación funciona.

---

## Constitution Check

*GATE: Verificación pre-implementación contra los 5 principios.*

| Principio                      | Estado | Notas                                                                          |
|--------------------------------|--------|--------------------------------------------------------------------------------|
| I. Data-First Analytics        | ✅     | `fact_shipment_request` existente no se modifica. Ninguna tabla del warehouse alterada. |
| II. Clean Layered Backend      | ✅     | Repository → Service → Router. Sin SQL en endpoints ni lógica en repositorio.  |
| III. Frontend–Backend Contract | ✅     | Frontend solo llama a `/shipments/*`. Sin DuckDB directo desde el frontend.    |
| IV. Containerized Portability  | ✅     | Sin hardcoding de rutas ni credenciales. Docker Compose no requiere cambios.   |
| V. Simplicity & YAGNI          | ✅     | Sin paginación, sin notificaciones, sin estados intermedios. Mínima complejidad.|

**Resultado**: PASS — sin violaciones. Puede proceder a implementación.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-shipments/
├── plan.md                        # Este archivo
├── spec.md                        # Especificación funcional
├── research.md                    # Decisiones técnicas y alternativas evaluadas
├── data-model.md                  # Schema de fact_shipment_request y reglas de validación
├── quickstart.md                  # Guía de validación end-to-end
├── contracts/
│   └── shipments-api.md           # Contratos POST, GET, PUT /shipments
└── tasks.md                       # Lista de tareas de implementación
```

### Source Code

```text
backend/
├── app/
│   ├── routers/                   # NUEVO directorio
│   │   └── shipments.py           # NUEVO: Router /shipments
│   ├── repositories/
│   │   └── shipment_repository.py # NUEVO: Queries DuckDB para fact_shipment_request
│   ├── schemas/
│   │   └── shipment.py            # NUEVO: ShipmentCreateRequest, ShipmentCancelRequest, ShipmentResponse
│   ├── services/
│   │   └── shipment_service.py    # NUEVO: Lógica de negocio (estados, validaciones, propiedad)
│   └── main.py                    # MODIFICAR: include_router(shipments_router)

frontend/
└── pages/
    └── shipments.py               # NUEVO: @ui.page('/shipments') — formulario + lista
```

**Archivos modificados** (mínimo):
- `backend/app/main.py` — añadir `include_router`
- `frontend/app.py` — añadir `import pages.shipments` y botón en sidebar para rol `cliente`

---

## Phase 0: Research

**Status**: COMPLETE — ver [research.md](research.md)

Decisiones resueltas:
- Tabla: `fact_shipment_request` existente — no modificar
- client_id: desde `app.storage.user['user_id']` en sesión
- Estados: `Pendiente → Cancelado` (cliente); otros en fases futuras
- Router: nuevo directorio `backend/app/routers/`
- Frontend: `frontend/pages/shipments.py` con `@ui.page('/shipments')`
- Arquitectura: Repository → Service → Router (igual que SPEC-001)

---

## Phase 1: Design & Contracts

**Status**: COMPLETE

Artefactos generados:
- [data-model.md](data-model.md) — Schema de `fact_shipment_request`, máquina de estados,
  reglas de validación
- [contracts/shipments-api.md](contracts/shipments-api.md) — Contratos POST /shipments/,
  GET /shipments/my y PUT /shipments/{id}/cancel con schemas Pydantic
- [quickstart.md](quickstart.md) — Escenarios de validación end-to-end

---

## Phase 2: Implementation

Ver [tasks.md](tasks.md).

**Orden de construcción**:

1. **Backend primero** (prerequisito para el frontend):
   - `schemas/shipment.py` — modelos Pydantic
   - `repositories/shipment_repository.py` — queries sobre `fact_shipment_request`
   - `services/shipment_service.py` — validaciones de negocio y estados
   - `routers/shipments.py` — endpoints REST
   - `main.py` — registrar el router

2. **Frontend segundo**:
   - `frontend/pages/shipments.py` — formulario + lista con acciones
   - `frontend/app.py` — import de la página + botón de sidebar para `cliente`

**Checkpoints de validación**:
1. `curl POST /shipments/` crea solicitud con estado "Pendiente" en `fact_shipment_request`
2. `curl GET /shipments/my` devuelve solo las solicitudes del cliente
3. `curl PUT /shipments/{id}/cancel` cambia el estado a "Cancelado"
4. `/shipments` en el navegador muestra formulario y lista correctamente
5. El botón "Cancelar" aparece solo en solicitudes "Pendiente"
6. Sin autenticación, `/shipments` redirige a `/login`

---

## Complexity Tracking

*No hay violaciones a la constitución que justificar.*
