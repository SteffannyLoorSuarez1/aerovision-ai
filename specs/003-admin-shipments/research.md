# Research: Panel de Envíos para Admin/Analista

**Branch**: `003-admin-shipments` | **Date**: 2026-06-25

---

## Decisiones técnicas

### 1. Cómo obtener el nombre del cliente junto con la solicitud

**Pregunta**: ¿JOIN en SQL o lookup en Python?

**Opción A — JOIN en SQL** (elegida):
```sql
SELECT s.*, u.nombre AS client_name, u.email AS client_email
FROM fact_shipment_request s
LEFT JOIN dim_users u ON s.client_id = u.id
ORDER BY s.request_id DESC
```
- Ventaja: una sola query, eficiente, datos consistentes.
- Desventaja: ninguna relevante para la escala actual.

**Opción B — lookup en Python**:
- Cargar solicitudes, luego hacer `SELECT nombre FROM dim_users WHERE id = ?` por cada fila.
- Ineficiente (N+1 queries). Descartada.

**Decisión**: LEFT JOIN en SQL. Si el cliente no existe (usuario eliminado), `client_name`
será NULL y se mostrará como "[Usuario eliminado]" en el frontend.

---

### 2. Dónde vive el nuevo endpoint

**Pregunta**: ¿Nuevo router o ampliar el existente `routers/shipments.py`?

**Decisión**: Ampliar `routers/shipments.py` con `GET /shipments/all`.
- Ya existe el prefijo `/shipments` en `main.py`.
- Mantiene cohesión: todos los endpoints de shipments en un solo lugar.
- No requiere registro de nuevo router en `main.py`.

---

### 3. Dónde vive la lógica en el frontend

**Pregunta**: ¿Nuevo archivo `pages/admin_shipments.py` o función en `app.py`?

**Decisión**: Función `show_admin_shipments()` en `frontend/app.py`, siguiendo
el patrón establecido de `show_dashboard()`, `show_import()`, etc.
- Consistente con el patrón del proyecto.
- Evita crear una página separada que perdería el sidebar.
- El filtrado por estado se implementa en el frontend sobre los datos ya cargados.

---

### 4. Filtrado — frontend vs backend

**Pregunta**: ¿Filtrar en backend (query con WHERE status=?) o en frontend?

**Decisión**: Cargar todos los datos al abrir el panel; filtrar en frontend cambiando
las filas del `ui.table` con `table.rows = [r for r in all_data if ...]`.
- Evita múltiples llamadas al backend por cambio de filtro.
- Escala bien para el volumen esperado (decenas/centenas de solicitudes).
- Patrón más simple sin estado adicional en el backend.

---

### 5. Esquema del response

**Nuevo modelo `AdminShipmentResponse`**:
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

- Se añade a `backend/app/schemas/shipment.py` (sin crear nuevo archivo).
- `client_name` y `client_email` provienen del JOIN con `dim_users`.
- `created_at` se convierte a string para evitar problemas de serialización de timestamp.

---

### 6. Rol analista — solo lectura

**Decisión**: La función `show_admin_shipments()` no tiene columna de acciones en
ningún rol en esta entrega. La distinción admin vs analista en acciones se implementa
en SPEC-007. En SPEC-003, ambos roles ven el mismo panel de solo lectura.

Esto simplifica la implementación y es consistente con el alcance de la spec.
