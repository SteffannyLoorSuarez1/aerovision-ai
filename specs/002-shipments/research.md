# Research: Solicitudes de Envío

**Feature**: 002-shipments
**Date**: 2026-06-25

---

## 1. Tabla fact_shipment_request — uso de tabla existente

**Decision**: No redefinir ni alterar `fact_shipment_request`. El módulo opera sobre la
tabla tal como existe en el warehouse.

**Rationale**:
- La constitución (Principio I) exige no modificar tablas analíticas existentes.
- `fact_shipment_request` fue diseñada para albergar solicitudes de envío; su schema
  ya cubre los campos requeridos por esta feature.
- La integridad del warehouse (fact_flights, fact_routes, etc.) no se ve afectada.

**Pattern**:
```python
# Repository lee y escribe sobre la tabla existente sin DDL
conn.execute(
    "INSERT INTO fact_shipment_request (...) VALUES (...)",
    [client_id, origin, destination, cargo_type, weight_kg, request_date, 'Pendiente']
)
```

**Alternatives considered**:
- Crear una tabla separada `dim_shipments` → descartado: la tabla ya existe y tiene el
  schema correcto; crear una duplicada viola YAGNI y genera inconsistencia.
- Añadir columnas nuevas a la tabla existente → descartado: la constitución prohíbe
  modificar tablas existentes del warehouse.

---

## 2. Identificación del cliente propietario

**Decision**: El `client_id` se extrae siempre de `app.storage.user['user_id']` en el
frontend y se pasa al backend en el cuerpo de la petición. El backend no acepta un
`client_id` diferente al del usuario autenticado.

**Rationale**:
- Evita que un cliente pueda crear o consultar solicitudes de otro cliente manipulando el
  cuerpo de la petición.
- Sigue el mismo patrón de sesión establecido en SPEC-001: `app.storage.user` es la
  fuente de verdad del usuario actual.

**Pattern**:
```python
# Frontend extrae el user_id de la sesión y lo incluye en el payload
user_id = app.storage.user.get('user_id')
resp = requests.post(
    f'{API_URL}/shipments/',
    json={..., 'client_id': user_id}
)

# Backend valida que client_id coincide con el usuario autenticado
# (en esta entrega, el frontend es la única fuente; la validación es en servicio)
```

**Alternatives considered**:
- Leer `client_id` exclusivamente en el backend vía token/header → descartado: la
  constitución prohíbe JWT y sesiones manejadas por el backend.
- Confiar únicamente en el `client_id` del body sin validación → descartado: vulnerabilidad
  IDOR (Insecure Direct Object Reference).

---

## 3. Máquina de estados de la solicitud

**Decision**: La solicitud tiene tres estados posibles: `Pendiente`, `Cancelado`, `Procesado`.
El cliente solo puede provocar la transición `Pendiente → Cancelado`. El resto de
transiciones pertenecen a módulos futuros.

**Estado inicial**: `Pendiente` — asignado automáticamente al crear.

**Transiciones permitidas en esta entrega**:

| Desde      | Hacia     | Actor   | Endpoint                    |
|------------|-----------|---------|----------------------------|
| (nuevo)    | Pendiente | sistema | POST /shipments/            |
| Pendiente  | Cancelado | cliente | PUT /shipments/{id}/cancel  |

**Rationale**:
- Modelo simple y extensible: los estados `Procesado`, `En tránsito`, etc. los gestionan
  módulos posteriores (cotización, reserva) sin necesidad de modificar esta feature.
- Validar el estado antes de cancelar evita doble cancelación y operaciones inconsistentes.

**Alternatives considered**:
- Boolean `cancelado` en lugar de campo `status` → descartado: no es extensible a más
  de dos estados.
- Enum con CHECK constraint en DuckDB → descartado: la tabla ya existe y no se modifica.

---

## 4. Ubicación del router — backend/app/routers/

**Decision**: Crear el router en `backend/app/routers/shipments.py` (nuevo subdirectorio
`routers/`), a diferencia de los routers existentes que están en `backend/app/api/`.

**Rationale**:
- El usuario del proyecto definió explícitamente la ruta `backend/app/routers/shipments.py`.
- Separar `routers/` de `api/` permite distinguir visualmente los módulos de negocio
  (shipments, quotations, reservations) de las APIs de catálogos e infraestructura.
- No es necesario mover los routers existentes de `api/`; conviven sin conflicto.

**Alternatives considered**:
- Añadir el router en `backend/app/api/shipments.py` → descartado: el usuario especificó
  `routers/` explícitamente.
- Un único archivo `backend/app/api/shipments.py` en el directorio ya existente → descartado
  por la misma razón.

---

## 5. Frontend — @ui.page('/shipments')

**Decision**: Crear `frontend/pages/shipments.py` con `@ui.page('/shipments')`. La página
verifica autenticación y rol `cliente` antes de mostrar contenido.

**Pattern**:
```python
# frontend/pages/shipments.py
from nicegui import ui, app as nicegui_app
from auth import check_auth, get_current_user

@ui.page('/shipments')
def shipments_page():
    if not check_auth():
        ui.navigate.to('/login')
        return
    user = get_current_user()
    # Renderizar formulario y lista...
```

**Rationale**:
- Sigue exactamente el mismo patrón de `frontend/pages/login.py` y `frontend/pages/register.py`
  establecido en SPEC-001.
- La importación en `frontend/app.py` registra la ruta sin modificar la lógica existente.

**Alternatives considered**:
- Añadir la página directamente en `frontend/app.py` → descartado: viola la constitución
  (Principio II) y agrava la deuda técnica del archivo de 2400+ líneas.
- Renderizar el formulario en la misma `/` con show/hide → descartado: no aísla el módulo
  y viola YAGNI.

---

## 6. Layered backend — Repository → Service → Router

**Decision**: Seguir la misma arquitectura en tres capas establecida en SPEC-001:
`shipment_repository.py` → `shipment_service.py` → `routers/shipments.py`.

**Capas**:

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Repository | `repositories/shipment_repository.py` | SQL sobre `fact_shipment_request` |
| Service | `services/shipment_service.py` | Validaciones de negocio, estados |
| Router | `routers/shipments.py` | Endpoints HTTP, serialización |

**Rationale**: La constitución (Principio II) exige esta separación. Sin ella, el SQL
en los endpoints impide testear la lógica de negocio de forma independiente.

**Alternatives considered**:
- SQL directamente en el router → descartado: viola Principio II de la constitución.
- Un único archivo `shipments.py` con todo → descartado: mismo motivo.

---

## Resumen de decisiones clave

| Tema                         | Decisión                                               |
|------------------------------|--------------------------------------------------------|
| Tabla BD                     | `fact_shipment_request` existente — no modificar       |
| Identificación del cliente   | `app.storage.user['user_id']` — fuente de verdad       |
| Estados de solicitud         | `Pendiente` → `Cancelado` (cliente); otros en futuras  |
| Ubicación del router         | `backend/app/routers/shipments.py` (nuevo directorio)  |
| Página frontend              | `frontend/pages/shipments.py` con `@ui.page`           |
| Arquitectura backend         | Repository → Service → Router (igual que SPEC-001)     |
