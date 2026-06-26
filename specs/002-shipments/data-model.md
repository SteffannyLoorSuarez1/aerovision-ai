# Data Model: Solicitudes de Envío

**Feature**: 002-shipments
**Date**: 2026-06-25

---

## Tabla principal — fact_shipment_request

> **IMPORTANTE**: Esta tabla ya existe en el Data Warehouse. **No debe redefinirse,
> recrearse ni alterarse.** El módulo opera sobre ella tal como está.

### Schema de referencia

```sql
-- Tabla existente — solo lectura del schema, NO ejecutar:
fact_shipment_request (
    request_id    INTEGER   PRIMARY KEY,
    client_id     INTEGER   NOT NULL,      -- FK → dim_users.id
    origin        VARCHAR   NOT NULL,
    destination   VARCHAR   NOT NULL,
    cargo_type    VARCHAR   NOT NULL,
    weight_kg     FLOAT     NOT NULL,
    request_date  DATE      NOT NULL,
    status        VARCHAR   NOT NULL,      -- 'Pendiente' | 'Cancelado' | 'Procesado'
    created_at    TIMESTAMP
)
```

**Restricciones de negocio** (validadas en la capa de servicio):
- `client_id` debe existir en `dim_users.id` y coincidir con el usuario autenticado.
- `weight_kg` debe ser positivo y mayor que cero.
- `status` solo acepta: `'Pendiente'`, `'Cancelado'`, `'Procesado'`.
  Validado en la capa de servicio (no a nivel de CHECK, para no modificar la tabla).
- `origin` y `destination` no pueden estar vacíos ni ser iguales entre sí.
- `request_date` no puede ser una fecha en el pasado (validación en servicio).

---

## Máquina de estados

```
  [NUEVO]
     │
     ▼
 Pendiente  ──(cliente cancela)──►  Cancelado
     │
     └──(módulos futuros)──►  Procesado
```

| Transición          | Actor        | Endpoint                  | Entrega    |
|---------------------|--------------|---------------------------|------------|
| → Pendiente         | Sistema      | POST /shipments/           | SPEC-002   |
| Pendiente→Cancelado | Cliente      | PUT /shipments/{id}/cancel | SPEC-002   |
| Pendiente→Procesado | Administrador| (futuro — cotización)     | SPEC futura|

---

## Tablas existentes (NO MODIFICAR)

Las siguientes tablas del warehouse permanecen intactas:

- `dim_airline`, `dim_airport`, `dim_airport_geo`, `dim_aircraft`, `dim_route`, `dim_date`
- `fact_flights`, `fact_airport_operations`, `fact_routes`
- `dim_users` (prerequisito — SPEC-001)

---

## Relación con dim_users

```
dim_users.id  ←──────────────────────  fact_shipment_request.client_id
(1 usuario)                             (N solicitudes)
```

Un usuario (`dim_users`) puede tener múltiples solicitudes (`fact_shipment_request`).
Cada solicitud pertenece a exactamente un cliente.

---

## Estado de sesión utilizado (frontend — no en BD)

El módulo lee los siguientes campos de `app.storage.user` (poblados por SPEC-001):

```python
app.storage.user = {
    'authenticated': True,       # bool — verificado en check_auth()
    'user_id': 1,                # int  — usado como client_id en los requests
    'nombre': 'Ana Torres',      # str  — mostrado en el encabezado de la página
    'rol': 'cliente'             # str  — verificado antes de mostrar el módulo
}
```

---

## Reglas de validación de negocio

| Campo          | Regla                                              | Nivel de validación |
|----------------|----------------------------------------------------|---------------------|
| client_id      | Siempre igual a `user_id` de la sesión activa      | Servicio            |
| origin         | No vacío, máx. 100 caracteres                      | Servicio            |
| destination    | No vacío, máx. 100 caracteres, ≠ origin            | Servicio            |
| cargo_type     | No vacío, máx. 100 caracteres                      | Servicio            |
| weight_kg      | Float, > 0                                         | Servicio + Schema   |
| request_date   | Fecha válida, no en el pasado                      | Servicio            |
| status (cancel)| Debe ser 'Pendiente' para permitir cancelación     | Servicio            |
| Propiedad      | client_id de la solicitud == user_id de la sesión  | Servicio            |

---

## Relaciones con tablas futuras

Las siguientes tablas de fases posteriores referenciarán `fact_shipment_request.request_id`:

| Tabla futura      | Campo FK    | Relación                                     |
|-------------------|-------------|----------------------------------------------|
| fact_quotation    | request_id  | Cada cotización corresponde a una solicitud  |
| fact_reservation  | request_id  | Cada reserva parte de una cotización aceptada|
| fact_satisfaction | request_id  | Encuesta vinculada al ciclo completo         |
