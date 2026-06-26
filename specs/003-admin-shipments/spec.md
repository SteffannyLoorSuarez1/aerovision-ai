# Feature Specification: Panel de Envíos para Admin/Analista

**Feature Branch**: `003-admin-shipments`

**Created**: 2026-06-25

**Status**: Draft

## Trazabilidad Empresarial

| Elemento | Valor |
|---|---|
| Nivel organizacional | Operativo / Táctico |
| Área/Departamento | Plataforma Digital — Gestión de Operaciones de Carga |
| Paquete del sistema | Módulo de Supervisión de Solicitudes (Admin Shipment Panel) |

### Casos de uso relacionados
- CU-O09: Consultar todas las solicitudes de envío (admin/analista)
- CU-O10: Filtrar solicitudes por estado
- CU-O11: Ver detalle de una solicitud con datos del cliente

### Conexión con niveles empresariales
- **Objetivo operativo**: Dar visibilidad completa a administradores y analistas sobre el flujo de solicitudes de carga en la plataforma
- **Objetivo táctico**: OT3 — Cerrar el ciclo de negocio del lado de la empresa: el cliente crea solicitudes, la empresa las gestiona
- **Objetivo estratégico**: OE2 — Convertir AeroVision en la plataforma operacional central del cargo aéreo

### Historias de usuario
US-008 → CU-O09 (Ver todas las solicitudes)
US-009 → CU-O10 (Filtrar solicitudes por estado)

**Input**: Panel administrativo de solicitudes de envío para roles administrador y analista de AeroVision AirCargo Exchange.

---

## User Scenarios & Testing *(mandatory)*

### User Story 8 — Ver todas las solicitudes de envío (Priority: P1)

Un administrador o analista autenticado puede ver el listado completo de todas las
solicitudes de envío registradas en la plataforma, de todos los clientes, incluyendo
el nombre y email del cliente propietario de cada solicitud.

**Why this priority**: Sin visibilidad de las solicitudes, la empresa no puede operar.
El cliente crea solicitudes pero la empresa no puede verlas; el flujo de negocio es
completamente unilateral. Esta es la brecha más crítica del sistema actual.

**Independent Test**: Un administrador autenticado abre el panel de envíos y ve todas
las solicitudes de todos los clientes con sus datos completos. Un analista autenticado
ve el mismo listado en modo solo lectura.

**Acceptance Scenarios**:

1. **Given** un administrador autenticado, **When** abre el panel "Gestión de Envíos",
   **Then** el sistema muestra todas las solicitudes de todos los clientes con los campos:
   ID, cliente (nombre), email del cliente, origen, destino, tipo de carga, peso, fecha y estado.
2. **Given** un analista autenticado, **When** abre el panel "Gestión de Envíos",
   **Then** el sistema muestra el mismo listado en modo solo lectura (sin acciones).
3. **Given** un cliente autenticado, **When** intenta acceder al panel de gestión,
   **Then** el botón no está visible en su sidebar y la vista no es accesible.
4. **Given** ninguna solicitud registrada, **When** el administrador abre el panel,
   **Then** el sistema muestra un mensaje indicando que no hay solicitudes.

---

### User Story 9 — Filtrar solicitudes por estado (Priority: P2)

Un administrador o analista autenticado puede filtrar el listado de solicitudes por
estado (Todas / Pendiente / Cancelado) para enfocarse en las solicitudes relevantes.

**Why this priority**: Con volumen creciente de solicitudes, filtrar por estado es
la operación más frecuente: el admin necesita ver solo las pendientes para actuar.

**Independent Test**: El administrador selecciona el filtro "Pendiente" y la tabla
muestra únicamente solicitudes con ese estado. Al seleccionar "Todas", vuelven a
aparecer todas las solicitudes.

**Acceptance Scenarios**:

1. **Given** un administrador con solicitudes en estados mixtos, **When** selecciona
   el filtro "Pendiente", **Then** la tabla muestra únicamente solicitudes con estado
   "Pendiente".
2. **Given** un administrador, **When** selecciona el filtro "Cancelado", **Then**
   la tabla muestra únicamente solicitudes con estado "Cancelado".
3. **Given** un administrador, **When** selecciona el filtro "Todas", **Then**
   la tabla muestra todas las solicitudes sin importar el estado.

---

### Edge Cases

- ¿Puede un cliente acceder al endpoint `GET /shipments/all`?
  → El endpoint no valida roles (patrón existente del proyecto). El control de acceso
  es frontend: el botón y la vista solo existen para admin/analista. Las solicitudes
  están protegidas de facto porque el cliente no tiene forma de llegar a ese endpoint
  desde la interfaz.
- ¿Qué ocurre si hay solicitudes de clientes eliminados (client_id huérfano)?
  → El JOIN con `dim_users` usa LEFT JOIN para evitar que solicitudes huérfanas
  desaparezcan del listado. Se muestra "[Usuario eliminado]" como nombre.
- ¿El panel se actualiza automáticamente?
  → No en esta entrega. El admin recarga manualmente usando un botón "Actualizar".
- ¿El analista puede realizar alguna acción sobre las solicitudes?
  → No. El analista tiene acceso de solo lectura. Sin botones de acción.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-028**: El sistema DEBE exponer un endpoint `GET /shipments/all` que devuelva
  todas las solicitudes de envío con datos del cliente (nombre, email) mediante JOIN
  con `dim_users`.
- **FR-029**: El endpoint DEBE soportar un parámetro opcional `status` para filtrar
  las solicitudes por estado.
- **FR-030**: El sistema DEBE mostrar el panel "Gestión de Envíos" únicamente en el
  sidebar de usuarios con rol `administrador` o `analista`.
- **FR-031**: El panel DEBE mostrar las columnas: ID, Cliente, Email, Origen, Destino,
  Tipo de carga, Peso (kg), Fecha, Estado.
- **FR-032**: El panel DEBE incluir un selector de filtro por estado (Todas / Pendiente /
  Cancelado) que filtra la tabla sin recargar la página.
- **FR-033**: El analista DEBE ver el listado en modo solo lectura, sin columna de
  acciones ni botones.
- **FR-034**: El administrador DEBE ver el listado con la misma vista que el analista
  en esta entrega. Las acciones sobre solicitudes se implementan en SPEC-007.
- **FR-035**: Si no hay solicitudes que coincidan con el filtro, el sistema DEBE mostrar
  un mensaje informativo.

### Key Entities

- **Panel administrativo de envíos**: vista del sistema que agrega todas las solicitudes
  con información del cliente propietario. Accesible para `administrador` y `analista`.
- **Filtro por estado**: selector UI que restringe las filas mostradas según el valor
  de la columna `status` de `fact_shipment_request`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-013**: Un administrador autenticado puede ver todas las solicitudes de todos los
  clientes, incluyendo el nombre del cliente, en menos de 3 segundos desde que abre el panel.
- **SC-014**: El filtro por estado restringe correctamente las filas: con filtro "Pendiente"
  solo aparecen solicitudes en ese estado; con "Todas" aparecen todas.
- **SC-015**: Un cliente autenticado NO puede acceder al panel administrativo desde el
  sidebar (el botón no existe para su rol).
- **SC-016**: El listado es idéntico para administrador y analista en esta entrega;
  la única diferencia futura será la columna de acciones (SPEC-007).
- **SC-017**: Solicitudes de clientes distintos aparecen en el mismo listado, correctamente
  asociadas al nombre y email de su propietario.

---

## Assumptions

- La tabla `fact_shipment_request` ya existe y no se modifica estructuralmente en esta entrega.
- La tabla `dim_users` ya existe con columnas `id`, `nombre`, `email`.
- El JOIN entre `fact_shipment_request.client_id` y `dim_users.id` es el mecanismo para
  obtener el nombre del cliente.
- No se implementan acciones sobre solicitudes (aprobar, rechazar, etc.) en esta entrega;
  esas funcionalidades pertenecen a SPEC-007.
- No hay paginación en el listado en esta entrega.
- El filtrado por estado se realiza en el frontend sobre los datos ya cargados
  (no requiere llamada adicional al backend por cada cambio de filtro).
- El control de acceso al endpoint `GET /shipments/all` es por convención de rol en
  el frontend, igual que todos los demás endpoints del proyecto.
- SPEC-001 y SPEC-002 están completadas como prerequisito.
