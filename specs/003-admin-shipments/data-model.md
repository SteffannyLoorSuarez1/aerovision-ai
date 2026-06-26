# Data Model: Panel de Envíos para Admin/Analista

**Branch**: `003-admin-shipments` | **Date**: 2026-06-25

---

## Tablas involucradas (sin modificaciones)

Esta spec no crea ni modifica tablas. Opera mediante JOIN de lectura sobre dos
tablas existentes.

### fact_shipment_request (existente — solo lectura)

| Columna       | Tipo      | Descripción                        |
|---------------|-----------|------------------------------------|
| request_id    | INTEGER   | PK — identificador de la solicitud |
| client_id     | INTEGER   | FK → dim_users.id                  |
| origin        | VARCHAR   | Código de ciudad/aeropuerto origen |
| destination   | VARCHAR   | Código de ciudad/aeropuerto destino|
| cargo_type    | VARCHAR   | Tipo de carga (texto libre)        |
| weight_kg     | FLOAT     | Peso en kilogramos (> 0)           |
| request_date  | DATE      | Fecha deseada de envío             |
| status        | VARCHAR   | Estado: Pendiente / Cancelado      |
| created_at    | TIMESTAMP | Timestamp de creación              |

### dim_users (existente — solo lectura, JOIN)

| Columna       | Tipo      | Descripción                        |
|---------------|-----------|------------------------------------|
| id            | INTEGER   | PK — identificador del usuario     |
| nombre        | VARCHAR   | Nombre completo del cliente        |
| email         | VARCHAR   | Email único del cliente            |
| rol           | VARCHAR   | Rol: cliente / administrador / analista |
| activo        | BOOLEAN   | Estado de la cuenta                |

---

## Query principal — GET /shipments/all

```sql
SELECT
    s.request_id,
    s.client_id,
    COALESCE(u.nombre, '[Usuario eliminado]') AS client_name,
    COALESCE(u.email,  '[sin email]')         AS client_email,
    s.origin,
    s.destination,
    s.cargo_type,
    s.weight_kg,
    s.request_date,
    s.status,
    CAST(s.created_at AS VARCHAR)             AS created_at
FROM fact_shipment_request s
LEFT JOIN dim_users u ON s.client_id = u.id
ORDER BY s.request_id DESC
```

**LEFT JOIN**: garantiza que solicitudes de clientes eliminados aparezcan en el listado
con valores por defecto en nombre y email.

**COALESCE**: convierte NULL a texto legible en la capa SQL para simplificar el frontend.

**CAST created_at AS VARCHAR**: evita problemas de serialización de timestamp en DuckDB.

---

## Modelo Pydantic — AdminShipmentResponse

Nuevo modelo añadido a `backend/app/schemas/shipment.py`:

```python
class AdminShipmentResponse(BaseModel):
    request_id:   int
    client_id:    int
    client_name:  str
    client_email: str
    origin:       str
    destination:  str
    cargo_type:   str
    weight_kg:    float
    request_date: date
    status:       str
    created_at:   str
```

---

## Estados válidos en esta entrega

| Estado     | Quién lo asigna | Descripción                        |
|------------|-----------------|------------------------------------|
| Pendiente  | Sistema         | Estado inicial al crear solicitud  |
| Cancelado  | Cliente         | Cliente canceló la solicitud       |

SPEC-007 añadirá: `Aprobado`, `En Tránsito`, `Entregado`, `Rechazado`.

---

## Relación entre tablas

```
dim_users.id  ←──────────────┐
                              │ LEFT JOIN
fact_shipment_request.client_id
```

No se crea FK formal (DuckDB no enforza FKs). El JOIN es por convención de datos.
