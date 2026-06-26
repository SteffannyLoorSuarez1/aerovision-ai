# AeroVision AirCargo Exchange — Constitución del Proyecto

**Version**: 1.0.0 | **Ratified**: 2026-06-24 | **Last Amended**: 2026-06-24

## Identidad del sistema
AeroVision AirCargo Exchange es una plataforma digital que conecta empresas con necesidades de transporte aéreo urgente con aerolíneas, usando inteligencia de datos históricos de puntualidad para seleccionar la opción más confiable y rentable. La propuesta de valor central es la certeza de entrega.

## Stack tecnológico (no cambiar sin autorización explícita)
- Frontend: NiceGUI (Python puro), puerto 8080
- Backend: FastAPI + Uvicorn, puerto 8000
- Base de datos: DuckDB (data-warehouse/warehouse.duckdb)
- Dataset: datasets/airline_2m.csv (~1.97M vuelos, 94 cols)
- Mapas: Leaflet (Operations Center), Google Charts GeoChart (Flight Map)
- Infraestructura: Docker Compose
- Encriptación: bcrypt (solo para contraseñas, sin JWT)

## Modelo de datos existente (NO modificar estas tablas)
Dimensiones existentes que deben conservarse intactas:
- dim_airline, dim_airport, dim_airport_geo, dim_aircraft, dim_route, dim_date

Hechos existentes que deben conservarse intactos:
- fact_flights (1.97M filas), fact_airport_operations, fact_routes

Problema conocido a NO propagar: fact_flights usa strings naturales en vez de surrogate keys, y métricas como VARCHAR. No refactorizar esto. Crear tablas nuevas con tipos correctos.

## Tablas nuevas a crear (con tipos correctos desde el inicio)
- dim_users: id, nombre, email, password_hash (bcrypt), rol (cliente/administrador/analista), fecha_creacion, activo (boolean)
- fact_reliability: airline_code, origin, destination, total_flights (INTEGER), delayed_flights (INTEGER), avg_delay_minutes (FLOAT), reliability_score (FLOAT), last_updated (TIMESTAMP)
- fact_shipment_request: id, client_id (FK dim_users), origin, destination, cargo_type, cargo_weight, requested_date, status, created_at
- fact_quotation: id, request_id, airline_code, reliability_score (FLOAT), estimated_price (FLOAT), risk_level (VARCHAR), created_at
- fact_reservation: id, quotation_id, client_id, status (confirmada/en_transito/entregada/cancelada), payment_status (pendiente/simulado_pagado), created_at
- fact_satisfaction: id, reservation_id, client_id, rating (INTEGER), comment (VARCHAR), created_at

## Roles de usuario
- cliente: cotiza, reserva, paga (simulado), da seguimiento, califica
- administrador: gestiona catálogos CRUD, importa datasets, ve todos los reportes
- analista: solo lectura — dashboard, DW, flight map, operations center

## Módulos existentes y su estado real
CONSERVAR Y NO ROMPER:
- Dashboard (95% completo)
- Operations Center (95% completo)
- CRUD Aerolíneas/Aeropuertos/Rutas/Aeronaves (85%, faltan UPDATE — agregarlos sin romper lo existente)
- Flight Map (40% — arreglar endpoint /warehouse/geo/airports para devolver los 500 aeropuertos, no 5 hardcodeados)
- Explorar Data Warehouse (30% — reemplazar hardcodes por consultas reales a la BD)
- Importar Dataset (5% — construir desde cero: endpoint real, parseo, validación, progreso)

## Flujo operativo principal (end-to-end)
Registro/login → solicitud de envío → cotización con scoring → ranking de aerolíneas → confirmar reserva → pago simulado → seguimiento del envío → encuesta de satisfacción

## Reglas de construcción (obligatorias)
1. Todo código nuevo va en archivos separados por módulo, no en frontend/app.py que ya tiene 1000+ líneas.
2. Las tablas nuevas usan tipos correctos (INTEGER, FLOAT, TIMESTAMP), nunca VARCHAR para métricas numéricas.
3. El scoring de riesgo es estadístico (% histórico de retrasos desde fact_flights), no un modelo ML entrenado.
4. Los pagos son simulados: marcan payment_status como 'simulado_pagado', sin Stripe ni pasarela real.
5. bcrypt para contraseñas, sin JWT, sin tokens de sesión complejos — sesión manejada por NiceGUI nativo.
6. Cada endpoint nuevo en FastAPI tiene su router propio en backend/app/routers/.
7. Antes de construir cualquier módulo, verificar que las tablas que necesita existen en DuckDB.
8. No hardcodear datos que deben venir de la BD.
9. Docker Compose debe seguir funcionando después de cada cambio.

## Alcance primera entrega (48 horas)
CONSTRUIR Y DEJAR FUNCIONANDO:
- Sistema de usuarios (registro, login, roles)
- Solicitud de envío (crear, consultar, cancelar)
- Cotización con scoring estadístico y ranking
- Confirmar reserva
- Pago simulado
- Seguimiento de envío
- Arreglar Flight Map (500 aeropuertos)
- Completar Explorar DW (datos reales)
- Completar Importar Dataset (funcional de verdad)
- UPDATE en los 4 CRUD

SIMULADO (no construir infraestructura real):
- Pagos: mock que marca como pagado
- Notificaciones: mostrar en UI sin email real

## Alcance segunda entrega (1 julio)
- Encuesta de satisfacción completa
- Historial de envíos con scoring real vs predicho
- Refinamiento de todos los módulos
- Reportes estratégicos desde el DW

## Lo que NUNCA debe hacer el agente
- Modificar dim_airline, dim_airport, dim_airport_geo, dim_aircraft, dim_route, dim_date, fact_flights, fact_airport_operations, fact_routes
- Cambiar el puerto del frontend (8080) ni del backend (8000)
- Instalar dependencias fuera del stack definido sin preguntar
- Borrar o sobreescribir frontend/app.py completo
- Crear pagos reales ni conectarse a pasarelas externas

## Governance
Esta constitución es la fuente de verdad del proyecto. Todo plan e implementación (especialmente vía /speckit-plan e /speckit-implement) debe verificar cumplimiento con estas reglas antes de generar código. Cualquier desviación debe documentarse y justificarse explícitamente. Enmiendas: actualizar versión, fecha de última modificación y notificar el cambio.