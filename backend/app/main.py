import duckdb

import os

if not os.path.exists("data-warehouse/warehouse.duckdb"):
    import app.core.init_warehouse

from app.core.database import conn
from fastapi import FastAPI
from app.api import ai

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
