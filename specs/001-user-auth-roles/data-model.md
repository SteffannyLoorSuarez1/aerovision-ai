# Data Model: Autenticación y Gestión de Usuarios

**Feature**: 001-user-auth-roles
**Date**: 2026-06-24

---

## Entidades nuevas

### dim_users

Almacena la identidad y credenciales de todos los usuarios de la plataforma.

```sql
CREATE SEQUENCE IF NOT EXISTS users_id_seq START 1;

CREATE TABLE IF NOT EXISTS dim_users (
    id             INTEGER   DEFAULT nextval('users_id_seq') PRIMARY KEY,
    nombre         VARCHAR   NOT NULL,
    email          VARCHAR   NOT NULL UNIQUE,
    password_hash  VARCHAR   NOT NULL,
    rol            VARCHAR   NOT NULL DEFAULT 'cliente',
    fecha_creacion TIMESTAMP DEFAULT current_timestamp,
    activo         BOOLEAN   DEFAULT true
);
```

**Restricciones**:
- `email` es único: no pueden existir dos usuarios con el mismo correo.
- `rol` acepta solo: `'cliente'`, `'administrador'`, `'analista'`.
  Validado en la capa de servicio (no a nivel de CHECK en DuckDB para mantener
  compatibilidad con versiones).
- `password_hash` NUNCA contiene la contraseña en texto plano; siempre es el hash
  bcrypt (60 caracteres).
- `activo = false` bloquea el acceso sin eliminar el registro.

**Índices**:
```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON dim_users(email);
```

---

## Tablas existentes (NO MODIFICAR)

Las siguientes tablas existentes permanecen intactas:

- `dim_airline`, `dim_airport`, `dim_airport_geo`, `dim_aircraft`, `dim_route`, `dim_date`
- `fact_flights`, `fact_airport_operations`, `fact_routes`

---

## Estado de sesión (frontend — no en BD)

La sesión activa se almacena en `app.storage.user` de NiceGUI (en memoria cifrada por
conexión). No persiste en DuckDB.

**Estructura del storage de sesión**:
```python
app.storage.user = {
    'authenticated': True,          # bool
    'user_id': 1,                   # int
    'nombre': 'Juan García',        # str
    'email': 'juan@example.com',    # str
    'rol': 'cliente'                # str: 'cliente' | 'administrador' | 'analista'
}
```

**Ciclo de vida**:
- Se pobla al hacer login exitoso.
- Se limpia (`app.storage.user.clear()`) al cerrar sesión.
- Se destruye al cerrar el navegador (comportamiento nativo de NiceGUI storage).

---

## Relaciones con tablas futuras

Las siguientes tablas de fases posteriores referenciarán `dim_users.id`:

| Tabla futura          | Campo FK         | Relación                         |
|-----------------------|------------------|----------------------------------|
| fact_shipment_request | client_id        | Cada solicitud pertenece a 1 cliente |
| fact_quotation        | (vía request_id) | Cotización vinculada a solicitud  |
| fact_reservation      | client_id        | Reserva pertenece a 1 cliente    |
| fact_satisfaction     | client_id        | Encuesta pertenece a 1 cliente   |

Estas tablas se crean en features posteriores; `dim_users` es su prerequisito.

---

## Reglas de validación de negocio

| Campo      | Regla                                          | Nivel de validación |
|------------|------------------------------------------------|---------------------|
| email      | Formato RFC 5321, único en sistema             | Servicio + BD       |
| password   | Mínimo 8 caracteres (antes de hashear)         | Servicio            |
| rol        | Solo: cliente / administrador / analista       | Servicio            |
| nombre     | No vacío, máx. 100 caracteres                  | Servicio            |
| activo     | false = acceso bloqueado sin borrar registro   | Servicio (login)    |
