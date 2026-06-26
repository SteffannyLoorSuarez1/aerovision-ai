# Quickstart: Panel de Envíos para Admin/Analista

**Branch**: `003-admin-shipments` | **Date**: 2026-06-25

---

## Prerequisitos

- Docker Compose corriendo: `docker compose up`
- Al menos una solicitud de envío existente (creada con usuario cliente)
- Usuario demo administrador: `adminaerovision@gmail.com` / `Admin2026!`
- Usuario demo analista: `analistaaerovision@gmail.com` / `Analista2026!`

---

## Escenario 1 — Admin ve todas las solicitudes

```bash
# Verificar que el endpoint existe y devuelve datos
curl http://localhost:8000/shipments/all
# → {"data": [{...solicitudes con client_name y client_email...}]}
```

**En el navegador**:
1. Abrir `http://localhost:8080`
2. Login como `adminaerovision@gmail.com`
3. Hacer clic en "📋 Gestión de Envíos" en el sidebar
4. Verificar que aparece la tabla con todas las solicitudes
5. Verificar que la columna "Cliente" muestra el nombre del cliente propietario

---

## Escenario 2 — Analista ve todas las solicitudes (solo lectura)

1. Login como `analistaaerovision@gmail.com`
2. Hacer clic en "📋 Gestión de Envíos" en el sidebar
3. Verificar que la tabla es idéntica a la del admin
4. Verificar que no hay columna de acciones ni botones de gestión

---

## Escenario 3 — Filtro por estado

1. Login como admin
2. Abrir "Gestión de Envíos"
3. Seleccionar filtro "Pendiente" en el selector de estado
4. Verificar que solo aparecen solicitudes con status "Pendiente"
5. Seleccionar "Todas"
6. Verificar que vuelven a aparecer todas las solicitudes

---

## Escenario 4 — Sin solicitudes

```bash
# Si la tabla está vacía
curl http://localhost:8000/shipments/all
# → {"data": []}
```

**En el navegador**: la tabla muestra "No hay solicitudes de envío registradas."

---

## Escenario 5 — Cliente no ve el panel

1. Login como usuario cliente (`cuentagpt9940@gmail.com` o cualquier cuenta registrada)
2. Verificar que el sidebar NO muestra el botón "Gestión de Envíos"
3. Solo debe aparecer "📦 Mis Envíos"

---

## Escenario 6 — Endpoint con filtro por status

```bash
# Solo pendientes
curl "http://localhost:8000/shipments/all?status=Pendiente"
# → {"data": [{...solo solicitudes Pendiente...}]}

# Solo canceladas
curl "http://localhost:8000/shipments/all?status=Cancelado"
# → {"data": [{...solo solicitudes Cancelado...}]}
```
