# API Contracts: Shipments

**Router prefix**: `/shipments`
**File**: `backend/app/routers/shipments.py`
**Tags**: `["Shipments"]`

---

## POST /shipments/

Crea una nueva solicitud de envío con estado "Pendiente".

### Request

```json
{
  "client_id":    "integer (required) — debe coincidir con user_id de la sesión",
  "origin":       "string (1-100 chars, required)",
  "destination":  "string (1-100 chars, required, ≠ origin)",
  "cargo_type":   "string (1-100 chars, required)",
  "weight_kg":    "float (> 0, required)",
  "request_date": "date string ISO 8601 YYYY-MM-DD (required, no pasado)"
}
```

**Pydantic schema**: `ShipmentCreateRequest` en `backend/app/schemas/shipment.py`

### Responses

**201 Created** — Solicitud creada:
```json
{
  "message":    "Solicitud de envío creada exitosamente",
  "request_id": 42
}
```

**400 Bad Request** — Validación de negocio fallida:
```json
{ "detail": "El origen y el destino no pueden ser iguales" }
```
```json
{ "detail": "La fecha de envío no puede ser en el pasado" }
```

**403 Forbidden** — client_id no coincide con el usuario autenticado:
```json
{ "detail": "No autorizado para crear solicitudes en nombre de otro cliente" }
```

**422 Unprocessable Entity** — Validación de schema fallida (peso ≤ 0, campos vacíos,
fecha con formato inválido). FastAPI lo genera automáticamente desde el schema Pydantic.

---

## GET /shipments/my

Devuelve todas las solicitudes de envío que pertenecen al cliente autenticado.
La identificación del cliente es responsabilidad de la capa de servicio, que obtiene
el `client_id` del contexto de la petición (enviado por el frontend desde la sesión activa).

### Responses

**200 OK** — Lista de solicitudes (puede ser vacía):
```json
{
  "data": [
    {
      "request_id":   42,
      "origin":       "BOG",
      "destination":  "MIA",
      "cargo_type":   "Farmacéutico",
      "weight_kg":    150.5,
      "request_date": "2026-07-10",
      "status":       "Pendiente"
    }
  ]
}
```

---

## PUT /shipments/{id}/cancel

Cancela una solicitud propia en estado "Pendiente".

### Path Parameter

| Parámetro | Tipo    | Descripción                    |
|-----------|---------|--------------------------------|
| `id`      | integer | ID de la solicitud a cancelar  |

### Request Body

```json
{
  "client_id": "integer (required) — user_id del cliente autenticado"
}
```

**Pydantic schema**: `ShipmentCancelRequest` en `backend/app/schemas/shipment.py`

### Responses

**200 OK** — Solicitud cancelada:
```json
{ "message": "Solicitud cancelada exitosamente" }
```

**403 Forbidden** — La solicitud no pertenece al cliente autenticado:
```json
{ "detail": "No autorizado para cancelar esta solicitud" }
```

**404 Not Found** — La solicitud no existe:
```json
{ "detail": "Solicitud no encontrada" }
```

**409 Conflict** — La solicitud no está en estado "Pendiente":
```json
{ "detail": "Solo se pueden cancelar solicitudes en estado Pendiente" }
```

---

## Pydantic Schemas (`backend/app/schemas/shipment.py`)

```python
from pydantic import BaseModel, field_validator
from datetime import date

class ShipmentCreateRequest(BaseModel):
    client_id:    int
    origin:       str
    destination:  str
    cargo_type:   str
    weight_kg:    float
    request_date: date

    @field_validator('weight_kg')
    @classmethod
    def weight_positive(cls, v):
        if v <= 0:
            raise ValueError('El peso debe ser mayor que cero')
        return v

    @field_validator('origin', 'destination', 'cargo_type')
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('El campo no puede estar vacío')
        return v.strip()

class ShipmentCancelRequest(BaseModel):
    client_id: int

class ShipmentResponse(BaseModel):
    request_id:   int
    origin:       str
    destination:  str
    cargo_type:   str
    weight_kg:    float
    request_date: date
    status:       str
```

---

## Notas de implementación

- **PUT en lugar de DELETE para cancelar**: la solicitud no se borra; solo cambia de estado.
  PUT es semánticamente correcto para una actualización de estado.
- **Error 403 vs 404 en cancelación**: si la solicitud existe pero no pertenece al cliente,
  se devuelve 403 (no 404) para no revelar la existencia de solicitudes ajenas.
- **Sin paginación**: GET /shipments/my devuelve todas las solicitudes del cliente en esta
  entrega. La paginación se añade en una fase posterior si el volumen lo requiere.
- **client_id en el body de POST y PUT, no en la URL**: exponer el ID del cliente en la URL
  facilitaría ataques de enumeración.
