# Requirements Checklist: Panel de Envíos para Admin/Analista

**Branch**: `003-admin-shipments` | **Date**: 2026-06-25

---

## Functional Requirements

- [ ] FR-028: `GET /shipments/all` devuelve todas las solicitudes con datos del cliente (JOIN con `dim_users`)
- [ ] FR-029: El endpoint soporta query param `status` para filtrar por estado
- [ ] FR-030: El panel "Gestión de Envíos" solo aparece en el sidebar de admin y analista
- [ ] FR-031: La tabla muestra: ID, Cliente, Email, Origen, Destino, Tipo de carga, Peso, Fecha, Estado
- [ ] FR-032: El selector de filtro por estado funciona sin recargar la página
- [ ] FR-033: El analista ve el listado en modo solo lectura (sin acciones)
- [ ] FR-034: El administrador ve el mismo listado de solo lectura (acciones en SPEC-007)
- [ ] FR-035: Sin solicitudes: mensaje "No hay solicitudes de envío registradas."

## Backend Requirements

- [ ] `AdminShipmentResponse` añadido a `schemas/shipment.py`
- [ ] `get_all_shipments()` añadido a `shipment_repository.py` con LEFT JOIN y COALESCE
- [ ] `get_all_shipments_service()` añadido a `shipment_service.py`
- [ ] `GET /all` añadido a `routers/shipments.py`
- [ ] Endpoints existentes de SPEC-002 sin modificaciones

## Frontend Requirements

- [ ] `show_admin_shipments()` añadida a `frontend/app.py`
- [ ] Botón `_b_admin_ship` visible solo para `administrador` y `analista`
- [ ] Filtro por estado actualiza `table.rows` sin llamada adicional al backend
- [ ] Error de conexión muestra `ui.notify` con `color='negative'`

## Access Control

- [ ] Cliente: botón "Gestión de Envíos" NO visible en sidebar
- [ ] Admin: botón visible, tabla con todas las solicitudes
- [ ] Analista: botón visible, tabla con todas las solicitudes (solo lectura)
