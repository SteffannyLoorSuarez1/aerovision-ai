# Quickstart: Autenticación y Gestión de Usuarios

**Feature**: 001-user-auth-roles
**Date**: 2026-06-24

---

## Prerequisites

```bash
docker compose up --build
```

Ambos servicios deben estar corriendo:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8080`

---

## Scenario 1: Registro exitoso (US1 — P1)

1. Abrir `http://localhost:8080/register`
2. Completar el formulario:
   - Nombre: `Ana Torres`
   - Email: `ana@test.com`
   - Contraseña: `mi_clave_123`
3. Hacer clic en "Registrarse"

**Resultado esperado**:
- Mensaje de éxito: "Usuario registrado exitosamente"
- Redirigido automáticamente a `http://localhost:8080/login`
- El registro en DuckDB existe:
  ```sql
  SELECT id, nombre, email, rol, activo FROM dim_users WHERE email = 'ana@test.com';
  -- id=1, nombre='Ana Torres', email='ana@test.com', rol='cliente', activo=true
  ```

---

## Scenario 2: Login y redirección por rol (US2 — P1)

### Cliente
1. Abrir `http://localhost:8080/login`
2. Email: `ana@test.com` | Contraseña: `mi_clave_123`
3. Hacer clic en "Iniciar sesión"

**Resultado esperado**:
- Redirigido a `http://localhost:8080/`
- Sidebar muestra solo los módulos de cliente (ningún botón de CRUD ni Import visible)
- Encabezado muestra: "Bienvenida, Ana Torres"

### Administrador
1. Login con cuenta `admin@aerovision.com` (creada manualmente en DuckDB)
2. **Resultado esperado**: Sidebar completo — Dashboard, Warehouse, CRUDs (4), Flight Map,
   Operations Center, Import Dataset

### Analista
1. Login con cuenta `analista@aerovision.com`
2. **Resultado esperado**: Sidebar muestra solo — Dashboard, Flight Map, Operations Center

---

## Scenario 3: Bloqueo de acceso no autorizado (US3 — P1)

1. Iniciar sesión como `ana@test.com` (rol: cliente)
2. Intentar navegar directamente a cualquier URL de módulo restringido
3. **Resultado esperado**: Pantalla de "Acceso denegado" o redirección a `/`
   sin mostrar contenido del módulo restringido

---

## Scenario 4: Cierre de sesión (US4 — P2)

1. Estar autenticado como cualquier usuario
2. Hacer clic en "Cerrar sesión" (botón en sidebar o encabezado)
3. **Resultado esperado**: Redirigido a `http://localhost:8080/login`
4. Presionar el botón "atrás" del navegador o navegar directamente a `/`
5. **Resultado esperado**: Redirigido de vuelta a `http://localhost:8080/login`
   (la sesión está invalidada)

---

## Scenario 5: Validaciones de registro (US1 edge cases)

| Caso de prueba                | Entrada                            | Resultado esperado                      |
|-------------------------------|------------------------------------|-----------------------------------------|
| Email duplicado               | Email ya registrado                | Error: "El email ya está registrado"    |
| Contraseña corta              | Password de 5 caracteres           | Error de validación antes de enviar     |
| Email inválido                | `no_es_email`                      | Error de validación de formato          |
| Nombre vacío                  | Nombre con solo espacios           | Error: "El nombre no puede estar vacío" |

---

## Scenario 6: Login fallido

| Caso de prueba           | Entrada                          | Resultado esperado                   |
|--------------------------|----------------------------------|--------------------------------------|
| Contraseña incorrecta    | Email correcto, pass incorrecto  | Error: "Credenciales inválidas"      |
| Email inexistente        | Email no registrado              | Error: "Credenciales inválidas"      |
| Cuenta desactivada       | activo=false en BD               | Error: "Cuenta desactivada"          |

---

## Verificación rápida de la API

```bash
# Registro
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test User","email":"test@x.com","password":"pass1234"}'
# Esperado: {"message":"Usuario registrado exitosamente","user_id":N}

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@x.com","password":"pass1234"}'
# Esperado: {"id":N,"nombre":"Test User","email":"test@x.com","rol":"cliente"}
```

---

## Referencias

- Data model: [data-model.md](data-model.md)
- API contracts: [contracts/users-api.md](contracts/users-api.md)
- Spec: [spec.md](spec.md)
