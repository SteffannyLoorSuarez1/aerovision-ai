# API Contract: Panel de Envíos para Admin/Analista

**Branch**: `003-admin-shipments` | **Date**: 2026-06-25

---

## Endpoints

### GET /shipments/all

Devuelve todas las solicitudes de envío de todos los clientes, con datos del cliente
propietario. Solo accesible para administrador y analista (control en frontend).

**Query Parameters** (todos opcionales):

| Parámetro | Tipo   | Descripción                                      |
|-----------|--------|--------------------------------------------------|
| status    | string | Filtrar por estado: `Pendiente` o `Cancelado`. Si se omite, devuelve todas. |

**Response 200 OK**:

```json
{
  "data": [
    {
      "request_id":   1,
      "client_id":    3,
      "client_name":  "Juan Pérez",
      "client_email": "juan@ejemplo.com",
      "origin":       "BOG",
      "destination":  "MIA",
      "cargo_type":   "General",
      "weight_kg":    120.5,
      "request_date": "2026-08-01",
      "status":       "Pendiente",
      "created_at":   "2026-06-25 10:30:00"
    }
  ]
}
```

**Response vacío (sin solicitudes)**:
```json
{ "data": [] }
```

**Notas**:
- `client_name` es `"[Usuario eliminado]"` si el cliente ya no existe en `dim_users`.
- `client_email` es `"[sin email]"` en el mismo caso.
- El listado está ordenado por `request_id DESC` (más recientes primero).
- No hay paginación en esta entrega.
- El filtrado por `status` en frontend reemplaza la necesidad de este query param
  en la mayoría de los casos; el param existe para uso directo de la API.

---

## Schemas Pydantic (backend)

### AdminShipmentResponse (nuevo — añadir a schemas/shipment.py)

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

## Sin cambios en endpoints existentes

Los endpoints de SPEC-002 no se modifican:

| Endpoint              | Estado   |
|-----------------------|----------|
| POST /shipments/      | Sin cambios |
| GET /shipments/my     | Sin cambios |
| PUT /shipments/{id}/cancel | Sin cambios |
