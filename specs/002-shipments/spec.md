# Feature Specification: Solicitudes de Envío

**Feature Branch**: `002-shipments`

**Created**: 2026-06-25

**Status**: Draft

## Trazabilidad Empresarial

| Elemento | Valor |
|---|---|
| Nivel organizacional | Operativo |
| Área/Departamento | Plataforma Digital — Gestión de Envíos |
| Paquete del sistema | Módulo de Solicitudes de Envío (Shipment Requests) |

### Casos de uso relacionados
- CU-O06: Crear solicitud de envío
- CU-O07: Consultar mis solicitudes de envío
- CU-O08: Cancelar una solicitud pendiente

### Conexión con niveles empresariales
- **Objetivo operativo**: Permitir al cliente registrar y gestionar sus solicitudes de carga aérea
- **Objetivo táctico**: OT2 — Digitalizar el proceso de admisión de carga (reducir fricción en el primer paso del ciclo de negocio)
- **Objetivo estratégico**: OE1 — Capturar masa crítica de clientes internacionales que generan solicitudes activas

### Historias de usuario
US-005 → CU-O06 (Crear solicitud)
US-006 → CU-O07 (Consultar solicitudes propias)
US-007 → CU-O08 (Cancelar solicitud pendiente)

**Input**: Módulo de solicitudes de envío para clientes autenticados de AeroVision AirCargo Exchange.

---

## User Scenarios & Testing *(mandatory)*

### User Story 5 — Crear solicitud de envío (Priority: P1)

Un cliente autenticado puede registrar una nueva solicitud de envío indicando el origen,
destino, tipo de carga, peso en kilogramos y fecha deseada. Al enviar, el sistema crea la
solicitud con estado "Pendiente" y la confirma inmediatamente.

**Why this priority**: La creación de solicitudes es el flujo de negocio principal del
cliente en la plataforma. Sin este flujo no hay transacciones posibles; es el punto de
entrada de la cadena de valor del cargo aéreo.

**Independent Test**: Un cliente autenticado puede abrir la página de envíos, completar
el formulario y recibir confirmación de que su solicitud fue registrada. La solicitud
aparece en la lista de "Mis solicitudes" con estado "Pendiente".

**Acceptance Scenarios**:

1. **Given** un cliente autenticado, **When** completa el formulario con origen, destino,
   tipo de carga, peso válido y fecha, y hace clic en "Crear solicitud", **Then** el sistema
   crea la solicitud con estado "Pendiente" y muestra mensaje de confirmación.
2. **Given** un cliente autenticado, **When** deja obligatorios vacíos (origen, destino,
   tipo de carga, peso o fecha) e intenta enviar, **Then** el sistema muestra errores de
   validación sin crear la solicitud.
3. **Given** un cliente autenticado, **When** introduce un peso negativo o igual a cero,
   **Then** el sistema rechaza el formulario con un mensaje de validación.

---

### User Story 6 — Consultar mis solicitudes de envío (Priority: P1)

Un cliente autenticado puede ver el listado completo de sus propias solicitudes de envío,
incluyendo origen, destino, tipo de carga, peso, fecha y estado actual de cada una.
El cliente no puede ver solicitudes de otros clientes.

**Why this priority**: El cliente necesita visibilidad sobre el estado de sus operaciones
en curso. Sin este flujo, la solicitud se convierte en una caja negra y el cliente no puede
hacer seguimiento.

**Independent Test**: Un cliente autenticado que ha creado al menos una solicitud puede
ver en la página de envíos la lista de sus solicitudes. Un cliente no ve solicitudes que
pertenecen a otro cliente.

**Acceptance Scenarios**:

1. **Given** un cliente autenticado con solicitudes previas, **When** abre la página de
   envíos, **Then** el sistema muestra únicamente sus solicitudes (no las de otros clientes)
   con todos sus campos y el estado actual.
2. **Given** un cliente autenticado sin solicitudes, **When** abre la página de envíos,
   **Then** el sistema muestra la lista vacía con un mensaje indicando que no hay solicitudes.
3. **Given** un cliente autenticado, **When** una solicitud cambia de estado, **Then** la
   lista refleja el estado actualizado al refrescar la página.

---

### User Story 7 — Cancelar una solicitud pendiente (Priority: P2)

Un cliente autenticado puede cancelar una solicitud propia que se encuentre en estado
"Pendiente". Las solicitudes en cualquier otro estado no pueden ser canceladas por el cliente.

**Why this priority**: La cancelación es un flujo secundario — el cliente ya obtuvo valor
al crear y consultar. Sin embargo, es necesaria para no dejar solicitudes activas que el
cliente no desea procesar.

**Independent Test**: Un cliente autenticado con una solicitud en estado "Pendiente" puede
hacer clic en "Cancelar" y la solicitud cambia su estado a "Cancelado". El botón "Cancelar"
no aparece para solicitudes en estados diferentes a "Pendiente".

**Acceptance Scenarios**:

1. **Given** un cliente autenticado con una solicitud en estado "Pendiente", **When** hace
   clic en "Cancelar", **Then** el sistema actualiza el estado a "Cancelado" y el botón
   desaparece de la fila.
2. **Given** un cliente autenticado con una solicitud en estado diferente a "Pendiente",
   **When** visualiza la lista de solicitudes, **Then** el botón "Cancelar" no está visible
   para esa solicitud.
3. **Given** un cliente autenticado, **When** intenta cancelar una solicitud que no le
   pertenece (acceso directo por ID), **Then** el sistema rechaza la operación con error
   de acceso no autorizado.

---

### Edge Cases

- ¿Qué ocurre si un cliente no autenticado intenta acceder a `/shipments`?
  → El sistema redirige automáticamente a `/login`.
- ¿Puede un administrador o analista crear solicitudes?
  → No; la creación de solicitudes es exclusiva del rol "cliente". Los otros roles no tienen
  acceso a esta página en esta entrega.
- ¿Puede un cliente ver o cancelar solicitudes de otro cliente?
  → No; el backend filtra siempre por el `client_id` del usuario autenticado.
- ¿Qué pasa si el cliente intenta cancelar una solicitud que ya está cancelada?
  → El backend responde con error 409 (Conflict); el botón de cancelar no debería mostrarse
  en ese estado, pero el backend valida igualmente.
- ¿Hay límite de solicitudes por cliente?
  → No en esta entrega.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-017**: El sistema DEBE permitir a un cliente autenticado crear una solicitud de envío
  con los campos: origen, destino, tipo de carga, peso (kg) y fecha de envío deseada.
- **FR-018**: El sistema DEBE asignar automáticamente el estado "Pendiente" a toda solicitud
  recién creada.
- **FR-019**: El sistema DEBE asociar automáticamente la solicitud al `client_id` del usuario
  autenticado que la crea, sin que el cliente lo especifique manualmente.
- **FR-020**: El sistema DEBE validar que origen, destino, tipo de carga y fecha no estén
  vacíos, y que el peso sea un número positivo mayor que cero.
- **FR-021**: El sistema DEBE permitir a un cliente autenticado consultar exclusivamente
  sus propias solicitudes de envío.
- **FR-022**: El sistema DEBE mostrar para cada solicitud: origen, destino, tipo de carga,
  peso, fecha y estado actual.
- **FR-023**: El sistema DEBE permitir a un cliente cancelar una solicitud propia únicamente
  si su estado es "Pendiente".
- **FR-024**: El sistema DEBE rechazar la cancelación de una solicitud cuyo estado no sea
  "Pendiente", devolviendo un error claro.
- **FR-025**: El sistema DEBE rechazar cualquier operación sobre solicitudes que no
  pertenezcan al cliente autenticado.
- **FR-026**: El sistema DEBE mostrar el botón "Cancelar" únicamente en solicitudes con
  estado "Pendiente"; las solicitudes en otros estados no presentan esa acción.
- **FR-027**: El sistema NO DEBE permitir a usuarios con rol "administrador" o "analista"
  crear, consultar ni cancelar solicitudes a través de este módulo en esta entrega.

### Key Entities

- **Solicitud de envío**: representa la intención de un cliente de transportar carga entre
  dos puntos. Atributos clave: cliente propietario, origen, destino, tipo de carga, peso,
  fecha de envío, estado (Pendiente / Cancelado / Procesado).
- **Estado de solicitud**: ciclo de vida de la solicitud. Transiciones permitidas al cliente:
  Pendiente → Cancelado. Las demás transiciones (Pendiente → Procesado) son responsabilidad
  de módulos posteriores.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-007**: Un cliente autenticado puede completar la creación de una solicitud en menos
  de 60 segundos desde que abre la página hasta recibir confirmación.
- **SC-008**: La lista "Mis solicitudes" no muestra nunca solicitudes de otros clientes;
  el filtrado por cliente es 100% efectivo.
- **SC-009**: El botón "Cancelar" aparece si y solo si la solicitud está en estado
  "Pendiente"; no aparece en ningún otro estado.
- **SC-010**: Una solicitud cancelada no puede volver a estado "Pendiente" por ninguna
  acción del cliente.
- **SC-011**: El backend rechaza el 100% de los intentos de operar sobre solicitudes de
  otro cliente, independientemente de si el acceso es por interfaz o por URL directa.
- **SC-012**: Un usuario no autenticado que intenta acceder a `/shipments` es redirigido
  a `/login` sin que se muestre ningún dato de solicitudes.

---

## Assumptions

- La tabla `fact_shipment_request` ya existe en el Data Warehouse y no debe redefinirse
  ni alterarse en esta entrega.
- El módulo es accesible exclusivamente para el rol "cliente"; administradores y analistas
  no utilizan este módulo en esta entrega.
- El estado "Procesado" lo asignan módulos posteriores (cotización, reserva); el cliente
  solo puede generar el estado "Cancelado".
- La autenticación y el control de sesión ya funcionan (prerequisito: SPEC-001 completada).
- El `client_id` se obtiene siempre de la sesión activa (`app.storage.user['user_id']`),
  nunca del cuerpo de la petición.
- No hay paginación en "Mis solicitudes" en esta entrega; se muestran todas las solicitudes
  del cliente sin límite.
- No hay notificaciones por email ni en tiempo real al crear o cancelar solicitudes.
- La fecha de envío es la fecha deseada por el cliente; no implica confirmación de disponibilidad.
