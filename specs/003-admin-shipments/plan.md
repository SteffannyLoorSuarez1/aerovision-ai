# Implementation Plan: Panel de Envíos para Admin/Analista

**Branch**: `003-admin-shipments` | **Date**: 2026-06-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-admin-shipments/spec.md`

---

## Summary

Implementar el panel administrativo de solicitudes de envío para AeroVision AirCargo
Exchange. Administradores y analistas podrán ver todas las solicitudes de todos los
clientes en una tabla centralizada, con filtros por estado. No se modifican tablas
existentes ni endpoints de SPEC-002. Esta entrega es solo lectura para ambos roles;
las acciones sobre solicitudes se implementan en SPEC-007.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI (backend), NiceGUI (frontend), DuckDB (almacenamiento),
Pydantic v2 (validación). Sin nuevas dependencias.

**Storage**: DuckDB — JOIN de lectura entre `fact_shipment_request` y `dim_users`.
No se crea ni modifica ninguna tabla.

**Testing**: Validación manual vía quickstart.md.

**Target Platform**: Linux container vía Docker Compose.

**Constraints**:
- No modificar endpoints existentes de SPEC-002.
- No crear nuevos archivos de router; ampliar `routers/shipments.py`.
- No crear nuevas páginas con `@ui.page`; usar el patrón `show_*()` de `app.py`.
- El filtrado por estado ocurre en el frontend sobre datos ya cargados.

**Prerequisito**: SPEC-001 y SPEC-002 completadas.

---

## Constitution Check

| Principio                      | Estado | Notas                                                                            |
|--------------------------------|--------|----------------------------------------------------------------------------------|
| I. Data-First Analytics        | ✅     | Solo lectura. Ninguna tabla se modifica. JOIN de lectura sobre datos existentes. |
| II. Clean Layered Backend      | ✅     | Nuevo método en repository → service → endpoint existente. Capas respetadas.    |
| III. Frontend–Backend Contract | ✅     | Frontend llama solo a `/shipments/all`. Sin acceso directo a DuckDB.            |
| IV. Containerized Portability  | ✅     | Sin hardcoding. Docker Compose sin cambios.                                      |
| V. Simplicity & YAGNI          | ✅     | Sin paginación, sin acciones, sin roles diferenciados en esta entrega.          |

**Resultado**: PASS — puede proceder a implementación.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-admin-shipments/
├── plan.md                          # Este archivo
├── spec.md                          # Especificación funcional
├── research.md                      # Decisiones técnicas
├── data-model.md                    # JOIN query y modelos Pydantic
├── quickstart.md                    # Guía de validación end-to-end
├── contracts/
│   └── admin-shipments-api.md       # Contrato GET /shipments/all
└── tasks.md                         # Lista de tareas de implementación
```

### Source Code — archivos a modificar

```text
backend/
└── app/
    ├── schemas/
    │   └── shipment.py              # MODIFICAR: añadir AdminShipmentResponse
    ├── repositories/
    │   └── shipment_repository.py   # MODIFICAR: añadir get_all_shipments()
    ├── services/
    │   └── shipment_service.py      # MODIFICAR: añadir get_all_shipments_service()
    └── routers/
        └── shipments.py             # MODIFICAR: añadir GET /all endpoint

frontend/
└── app.py                           # MODIFICAR: añadir show_admin_shipments() + botón sidebar
```

**Archivos nuevos**: ninguno.
**Archivos modificados**: 5 (los mismos de SPEC-002 más `frontend/app.py` para el panel).

---

## Phase 0: Research

**Status**: COMPLETE — ver [research.md](research.md)

Decisiones resueltas:
- JOIN LEFT entre `fact_shipment_request` y `dim_users` para obtener datos del cliente
- Ampliar `routers/shipments.py` (no crear nuevo router)
- Función `show_admin_shipments()` en `frontend/app.py` (no nueva página)
- Filtrado por estado en el frontend sobre datos cargados
- Nuevo Pydantic model `AdminShipmentResponse` en `schemas/shipment.py`
- Ambos roles (admin y analista) con vista idéntica de solo lectura en esta entrega

---

## Phase 1: Design & Contracts

**Status**: COMPLETE

Artefactos generados:
- [data-model.md](data-model.md) — Query JOIN y modelo AdminShipmentResponse
- [contracts/admin-shipments-api.md](contracts/admin-shipments-api.md) — Contrato GET /shipments/all
- [quickstart.md](quickstart.md) — Escenarios de validación end-to-end

---

## Phase 2: Implementation

Ver [tasks.md](tasks.md).

**Orden de construcción**:

1. **Backend primero**:
   - `schemas/shipment.py` — añadir `AdminShipmentResponse`
   - `repositories/shipment_repository.py` — añadir `get_all_shipments()`
   - `services/shipment_service.py` — añadir `get_all_shipments_service()`
   - `routers/shipments.py` — añadir `GET /all`

2. **Frontend segundo**:
   - `frontend/app.py` — añadir `show_admin_shipments()` y botón sidebar

**Checkpoints de validación**:
1. `curl GET /shipments/all` devuelve todas las solicitudes con `client_name` y `client_email`
2. `curl GET /shipments/all?status=Pendiente` devuelve solo pendientes
3. Panel visible en sidebar para admin y analista; no visible para cliente
4. Filtro de estado en el panel funciona sin recargar la página

---

## Complexity Tracking

*Sin violaciones a la constitución. La única complejidad es el JOIN LEFT que requiere
COALESCE para manejar clientes eliminados — documentado en data-model.md.*
