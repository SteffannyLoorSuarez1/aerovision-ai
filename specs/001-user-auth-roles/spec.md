# Feature Specification: Autenticación y Gestión de Usuarios

**Feature Branch**: `001-user-auth-roles`

**Created**: 2026-06-24

**Status**: Draft

## Trazabilidad Empresarial

| Elemento | Valor |
|---|---|
| Nivel organizacional | Operativo |
| Área/Departamento | Plataforma Digital — Gestión de Acceso |
| Paquete del sistema | Módulo de Autenticación y Usuarios |

### Casos de uso relacionados
- CU-O01: Registrar usuario (cliente)
- CU-O02: Iniciar sesión con redirección por rol
- CU-O03: Controlar acceso por rol
- CU-O04: Cerrar sesión
- CU-O05: Gestionar usuarios (administrador asigna roles)

### Conexión con niveles empresariales
- **Objetivo operativo**: Registrar usuarios y gestionar acceso por roles
- **Objetivo táctico**: OT1 — Implementar embudos de captación digital (el registro es el punto de entrada del cliente)
- **Objetivo estratégico**: OE1 — Capturar masa crítica de clientes internacionales

### Historias de usuario
US-001 → CU-O01 (Registro)
US-002 → CU-O02 (Login con rol)
US-003 → CU-O03 (Control de acceso)
US-004 → CU-O04 (Cierre de sesión)

**Input**: Sistema de autenticación y gestión de usuarios para AeroVision AirCargo Exchange.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Registro de nuevo usuario (Priority: P1)

Un visitante que desea usar la plataforma puede crear una cuenta proporcionando su nombre
completo, dirección de correo electrónico y contraseña. Al completar el registro exitosamente,
el sistema crea su perfil con el rol "cliente" y lo redirige a la pantalla de inicio de sesión.

**Why this priority**: Sin registro no hay acceso a ningún módulo de la plataforma. Es el
punto de entrada obligatorio para todos los usuarios nuevos.

**Independent Test**: Un visitante sin cuenta puede navegar a la pantalla de registro,
completar el formulario y recibir confirmación de que su cuenta fue creada. El registro
entrega valor inmediato como puerta de entrada a la plataforma.

**Acceptance Scenarios**:

1. **Given** un visitante sin cuenta, **When** completa el formulario con nombre, email válido
   y contraseña de al menos 8 caracteres y envía, **Then** el sistema crea la cuenta con rol
   "cliente" y muestra mensaje de éxito.
2. **Given** un visitante, **When** intenta registrarse con un email ya existente en el sistema,
   **Then** el sistema muestra un error indicando que el email ya está en uso.
3. **Given** un visitante, **When** introduce una contraseña de menos de 8 caracteres o un
   email con formato inválido, **Then** el sistema muestra el error de validación correspondiente
   antes de enviar el formulario.

---

### User Story 2 — Inicio de sesión con redirección por rol (Priority: P1)

Un usuario registrado puede iniciar sesión con su email y contraseña. El sistema verifica
sus credenciales, identifica su rol y lo redirige automáticamente a la vista principal que
le corresponde según su perfil.

**Why this priority**: El acceso autenticado es prerequisito para cualquier operación en
la plataforma. La redirección por rol elimina pasos manuales y reduce errores de navegación.

**Independent Test**: Un usuario con cuenta existente puede ingresar sus credenciales y
llegar a su vista de rol sin intervención manual. Cada rol (cliente, administrador, analista)
llega a su pantalla correcta.

**Acceptance Scenarios**:

1. **Given** un usuario con cuenta activa, **When** ingresa email y contraseña correctos,
   **Then** el sistema lo autentica y redirige a la vista correspondiente a su rol.
2. **Given** un usuario, **When** ingresa contraseña incorrecta o email inexistente,
   **Then** el sistema muestra un mensaje de error genérico sin revelar cuál campo es incorrecto.
3. **Given** un usuario con cuenta desactivada, **When** intenta iniciar sesión, **Then**
   el sistema rechaza el acceso con mensaje de cuenta inactiva.

---

### User Story 3 — Control de acceso por rol (Priority: P1)

Una vez autenticado, cada usuario solo puede ver y acceder a los módulos que corresponden
a su rol. Cualquier intento de acceder a un módulo no permitido es bloqueado con un mensaje
claro.

**Why this priority**: Sin control de acceso, cualquier usuario podría acceder a funciones
administrativas o a datos restringidos, comprometiendo la integridad del sistema.

**Independent Test**: Un usuario con rol "analista" que intenta navegar directamente al
módulo de CRUD de catálogos recibe una pantalla de acceso denegado. Un "cliente" no ve
las opciones de administración en el menú.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado como "cliente", **When** navega por la plataforma,
   **Then** solo ve y puede acceder a: solicitud de envío, cotización, reservas, seguimiento
   y calificación.
2. **Given** un usuario autenticado como "administrador", **When** navega por la plataforma,
   **Then** tiene acceso a todos los módulos del cliente más CRUD de catálogos e importación
   de datos.
3. **Given** un usuario autenticado como "analista", **When** navega por la plataforma,
   **Then** solo puede acceder a dashboard, mapa de vuelos y centro de operaciones (solo lectura).
4. **Given** cualquier usuario autenticado, **When** intenta acceder directamente a un módulo
   fuera de su rol, **Then** el sistema bloquea el acceso y muestra un mensaje de acceso
   denegado.

---

### User Story 4 — Cierre de sesión (Priority: P2)

Un usuario autenticado puede cerrar sesión desde cualquier pantalla de la plataforma. Al
cerrar sesión, la sesión queda completamente invalidada y el sistema lo redirige a la
pantalla de inicio de sesión.

**Why this priority**: Necesario para compartir dispositivos y para seguridad básica.
Es un flujo secundario una vez que el acceso ya funciona.

**Independent Test**: Un usuario autenticado hace clic en "Cerrar sesión" y posteriormente
intenta navegar a una página protegida; el sistema lo redirige al login en vez de mostrar
el contenido.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** hace clic en "Cerrar sesión", **Then** la
   sesión se invalida y el sistema redirige a la pantalla de login.
2. **Given** un usuario que cerró sesión, **When** intenta acceder directamente a una URL
   de un módulo protegido, **Then** el sistema lo redirige al login.

---

### Edge Cases

- ¿Qué pasa cuando se intenta registrar con un email ya existente?
  → El sistema muestra error específico indicando que el email ya está registrado.
- ¿Cómo maneja el sistema múltiples intentos de login fallidos?
  → No hay bloqueo automático en esta entrega; los intentos fallidos muestran el mismo
  mensaje de error genérico.
- ¿Qué ocurre si un usuario activo es desactivado mientras tiene sesión abierta?
  → La sesión actual permanece activa hasta que el usuario cierre sesión o la sesión
  expire naturalmente.
- ¿Qué ve un usuario no autenticado que intenta acceder a una URL protegida?
  → El sistema redirige automáticamente a la pantalla de login.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir a cualquier visitante crear una cuenta con nombre
  completo, email y contraseña.
- **FR-002**: El sistema DEBE rechazar el registro si el email ya existe en la base de
  datos de usuarios, mostrando un mensaje de error claro.
- **FR-003**: El sistema DEBE validar que el email tenga formato válido y que la contraseña
  tenga al menos 8 caracteres antes de crear la cuenta.
- **FR-004**: El sistema DEBE almacenar contraseñas de forma irreversible; en ningún
  momento una contraseña puede estar recuperable en texto plano.
- **FR-005**: El sistema DEBE asignar el rol "cliente" de forma automática a todo usuario
  que se registre a través del formulario público.
- **FR-006**: El sistema DEBE permitir a usuarios registrados iniciar sesión con su email
  y contraseña.
- **FR-007**: El sistema DEBE mostrar un mensaje de error genérico ante credenciales
  incorrectas, sin indicar cuál de los dos campos es el erróneo.
- **FR-008**: El sistema DEBE rechazar el acceso a usuarios con cuenta desactivada.
- **FR-009**: El sistema DEBE redirigir automáticamente al usuario tras el login a la
  vista principal correspondiente a su rol.
- **FR-010**: El rol "cliente" DEBE dar acceso exclusivamente a: solicitud de envío,
  cotización, reservas, seguimiento de envíos y calificación.
- **FR-011**: El rol "administrador" DEBE dar acceso a todos los módulos del cliente más
  gestión de catálogos (CRUD) e importación de datos.
- **FR-012**: El rol "analista" DEBE dar acceso exclusivamente a: dashboard, mapa de
  vuelos y centro de operaciones, todos en modo solo lectura.
- **FR-013**: El sistema DEBE bloquear el acceso a cualquier módulo no permitido para el
  rol del usuario autenticado, incluso si intenta acceder directamente por URL.
- **FR-014**: El sistema DEBE ofrecer la opción de cerrar sesión desde cualquier pantalla
  autenticada.
- **FR-015**: Al cerrar sesión, el sistema DEBE invalidar la sesión activa e impedir
  cualquier acceso posterior sin nueva autenticación.
- **FR-016**: Los roles "administrador" y "analista" DEBEN ser asignados únicamente de
  forma manual por un administrador existente (no son seleccionables en el registro público).

### Key Entities

- **Usuario**: representa a la persona que interactúa con la plataforma. Atributos clave:
  nombre completo, correo electrónico (único e identificador de acceso), contraseña
  (almacenada de forma irreversible), rol (cliente / administrador / analista), estado
  activo/inactivo, fecha de registro.
- **Sesión**: período activo de conexión de un usuario autenticado. Se crea al iniciar
  sesión exitosamente y se destruye al cerrar sesión o al cerrar la aplicación.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un visitante puede completar el proceso de registro en menos de 2 minutos
  desde que abre la pantalla de registro hasta recibir confirmación de cuenta creada.
- **SC-002**: Un usuario registrado puede iniciar sesión y llegar a la vista de su rol
  en menos de 10 segundos desde que envía el formulario de login.
- **SC-003**: El 100% de los intentos de acceso a módulos no permitidos son bloqueados,
  independientemente de si el usuario llega por menú o por URL directa.
- **SC-004**: Ninguna contraseña almacenada puede ser recuperada en texto plano por ningún
  medio (administrador, base de datos, logs).
- **SC-005**: Un usuario que cierra sesión no puede acceder a ningún módulo protegido sin
  volver a autenticarse, incluso si regresa con el botón "atrás" del navegador.
- **SC-006**: Cada rol (cliente, administrador, analista) ve exclusivamente los módulos
  que le corresponden; no hay módulos adicionales ni faltantes en su vista.

---

## Assumptions

- El rol predeterminado para cualquier registro público es "cliente"; los roles
  "administrador" y "analista" se asignan únicamente de forma manual.
- La recuperación de contraseña olvidada queda fuera del alcance de esta entrega.
- La verificación de email por correo electrónico queda fuera del alcance de esta entrega.
- La sesión se invalida al cerrar sesión manualmente o al cerrar la aplicación; no hay
  expiración por tiempo de inactividad en esta entrega.
- Un usuario solo puede tener un rol activo a la vez.
- La gestión de usuarios por parte del administrador (crear usuarios con otros roles,
  desactivar cuentas, cambiar roles) es parte del módulo de CRUD de catálogos y no de
  esta feature.
- No existe límite de intentos de login ni bloqueo temporal por intentos fallidos en
  esta entrega.
- La plataforma asume que el usuario accede desde un navegador moderno en un dispositivo
  de escritorio; no se requiere optimización para móvil en esta entrega.
