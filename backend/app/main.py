import duckdb
import os
import bcrypt

if not os.path.exists("data-warehouse/warehouse.duckdb"):
    import app.core.init_warehouse

from app.core.database import conn
from fastapi import FastAPI
from app.api import ai
from app.api.users import router as users_router
from app.routers.shipments import router as shipments_router

from app.api.warehouse import (
    router as warehouse_router
)

from app.api.airline import (
    router as airline_router
)

from app.api.airport import (
    router as airport_router
)

from app.api.operations import (
    router as operations_router
)

from app.api.routes import (
    router as routes_router
)

from app.api.operations_routes import (
    router as operations_routes_router
)
from app.api.aircraft import (
    router as aircraft_router
)
# =====================================================
# FASTAPI
# =====================================================


    
app = FastAPI(
    title="AeroVision AI",
    version="1.0.0"
)


@app.on_event("startup")
def init_users_table():
    conn.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq START 1")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_users (
            id             INTEGER   DEFAULT nextval('users_id_seq') PRIMARY KEY,
            nombre         VARCHAR   NOT NULL,
            email          VARCHAR   NOT NULL UNIQUE,
            password_hash  VARCHAR   NOT NULL,
            rol            VARCHAR   NOT NULL DEFAULT 'cliente',
            fecha_creacion TIMESTAMP DEFAULT current_timestamp,
            activo         BOOLEAN   DEFAULT true
        )
    """)
    seed_demo_users()


def seed_demo_users():
    demo = [
        ("Administrador", "adminaerovision@gmail.com", "Admin2026!", "administrador"),
        ("Analista", "analistaaerovision@gmail.com", "Analista2026!", "analista"),
    ]

    for nombre, email, password, rol in demo:
        pw_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        exists = conn.execute(
            "SELECT id FROM dim_users WHERE email = ?",
            [email]
        ).fetchone()

        if exists is None:
            new_id = conn.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 FROM dim_users WHERE id IS NOT NULL"
            ).fetchone()[0]

            conn.execute(
                """
                INSERT INTO dim_users
                (id, nombre, email, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, ?, true)
                """,
                [new_id, nombre, email, pw_hash, rol],
            )
        else:
            conn.execute(
                """
                UPDATE dim_users
                SET nombre        = ?,
                    password_hash = ?,
                    rol           = ?,
                    activo        = true
                WHERE email = ?
                """,
                [nombre, pw_hash, rol, email],
            )


@app.on_event("startup")
def init_shipments_table():
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fact_shipment_request (
            request_id   INTEGER   PRIMARY KEY,
            client_id    INTEGER   NOT NULL,
            origin       VARCHAR   NOT NULL,
            destination  VARCHAR   NOT NULL,
            cargo_type   VARCHAR   NOT NULL,
            weight_kg    FLOAT     NOT NULL,
            request_date DATE      NOT NULL,
            status       VARCHAR   NOT NULL DEFAULT 'Pendiente',
            created_at   TIMESTAMP DEFAULT current_timestamp
        )
    """)

# =====================================================
# ROUTERS
# =====================================================

app.include_router(
    warehouse_router,
    prefix="/warehouse",
    tags=["Warehouse"]
)

app.include_router(
    airline_router,
    prefix="/airlines",
    tags=["Airlines"]
)

app.include_router(
    airport_router,
    prefix="/airports",
    tags=["Airports"]
)

app.include_router(
    aircraft_router,
    prefix="/aircraft",
    tags=["Aircraft"]
)

app.include_router(
    operations_router
)



app.include_router(
    routes_router,
    tags=["Routes"]
)


app.include_router(
    operations_routes_router
)

app.include_router(
    ai.router
)

app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    shipments_router,
    prefix="/shipments",
    tags=["Shipments"]
)

# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():

    return {
        "message": "AeroVision AI Backend Running"
    }

# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "system": "AeroVision AI",
        "backend": "running"
    }
