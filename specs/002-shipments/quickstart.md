# Quickstart: Solicitudes de Envío

**Feature**: 002-shipments
**Date**: 2026-06-25

---

## Prerequisites

```bash
docker compose up --build
```

Ambos servicios deben estar corriendo:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8080`

SPEC-001 completada: existe al menos un usuario con rol `cliente` en `dim_users`.

---

## Scenario 1: Crear solicitud de envío (US5 — P1)

1. Abrir `http://localhost:8080/login`
2. Iniciar sesión con una cuenta de rol `cliente`
3. Navegar a `http://localhost:8080/shipments` (o usar el botón del sidebar)
4. Completar el formulario:
   - Origen: `BOG`
   - Destino: `MIA`
   - Tipo de carga: `Farmacéutico`
   - Peso (kg): `150.5`
   - Fecha: (fecha futura)
5. Hacer clic en "Crear solicitud"

**Resultado esperado**:
- Mensaje de confirmación: "Solicitud de envío creada exitosamente"
- La solicitud aparece en la lista "Mis solicitudes" con estado `Pendiente`

**Verificación vía API**:
```bash
curl -X POST http://localhost:8000/shipments/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "origin": "BOG",
    "destination": "MIA",
    "cargo_type": "Farmacéutico",
    "weight_kg": 150.5,
    "request_date": "2026-08-01"
  }'
# Esperado: {"message": "Solicitud de envío creada exitosamente", "request_id": N}
```

---

## Scenario 2: Consultar mis solicitudes (US6 — P1)

1. Estar autenticado como `cliente`
2. Abrir `http://localhost:8080/shipments`

**Resultado esperado**:
- La lista muestra solo las solicitudes del cliente autenticado
- Cada fila muestra: origen, destino, tipo de carga, peso, fecha y estado
- No aparecen solicitudes de otros clientes

**Verificación vía API**:
```bash
curl -X GET http://localhost:8000/shipments/my \
  -H "Content-Type: application/json"
# Esperado: {"data": [{...}, {...}]} — solo solicitudes del cliente
```

---

## Scenario 3: Cancelar una solicitud pendiente (US7 — P2)

1. Estar autenticado como `cliente` con al menos una solicitud en estado `Pendiente`
2. En la lista "Mis solicitudes", localizar una fila con estado `Pendiente`
3. Hacer clic en el botón "Cancelar" de esa fila

**Resultado esperado**:
- Mensaje de confirmación: "Solicitud cancelada exitosamente"
- El estado de la solicitud cambia a `Cancelado` en la lista
- El botón "Cancelar" desaparece de esa fila

**Verificación vía API**:
```bash
curl -X PUT http://localhost:8000/shipments/42/cancel \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1}'
# Esperado: {"message": "Solicitud cancelada exitosamente"}
```

---

## Scenario 4: Botón "Cancelar" solo visible en estado Pendiente

1. Tener solicitudes en diferentes estados: `Pendiente`, `Cancelado`
2. Abrir `http://localhost:8080/shipments`

**Resultado esperado**:
- Las filas con estado `Pendiente` muestran el botón "Cancelar"
- Las filas con estado `Cancelado` o `Procesado` NO muestran el botón "Cancelar"

---

## Scenario 5: Acceso sin autenticación

1. Cerrar sesión (o abrir en ventana de incógnito)
2. Navegar directamente a `http://localhost:8080/shipments`

**Resultado esperado**:
- Redirigido automáticamente a `http://localhost:8080/login`
- No se muestra ningún dato de solicitudes

---

## Scenario 6: Validaciones del formulario

| Caso de prueba            | Entrada                          | Resultado esperado                              |
|---------------------------|----------------------------------|-------------------------------------------------|
| Peso negativo             | Peso: `-10`                      | Error de validación — peso debe ser mayor que 0 |
| Peso cero                 | Peso: `0`                        | Error de validación — peso debe ser mayor que 0 |
| Origen vacío              | Origen: ` ` (espacios)           | Error de validación — campo requerido           |
| Origen = Destino          | Origen: `BOG`, Destino: `BOG`    | Error: "El origen y el destino no pueden ser iguales" |
| Fecha en el pasado        | Fecha: `2020-01-01`              | Error: "La fecha de envío no puede ser en el pasado" |

---

## Scenario 7: Cancelación de solicitud ya cancelada

1. Tener una solicitud en estado `Cancelado`
2. Intentar cancelarla nuevamente vía API

```bash
curl -X PUT http://localhost:8000/shipments/42/cancel \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1}'
# Esperado: 409 {"detail": "Solo se pueden cancelar solicitudes en estado Pendiente"}
```

---

## Referencias

- Data model: [data-model.md](data-model.md)
- API contracts: [contracts/shipments-api.md](contracts/shipments-api.md)
- Spec: [spec.md](spec.md)
