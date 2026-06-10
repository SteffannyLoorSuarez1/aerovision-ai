from fastapi import APIRouter
from pydantic import BaseModel
from app.core.database import conn

router = APIRouter()

# =====================================================
# MODEL
# =====================================================

class RouteCreate(BaseModel):

    origin_code: str
    destination_code: str
    avg_distance: float

# =====================================================
# GET ROUTES
# =====================================================

@router.get("/routes")

def get_routes():

    data = conn.execute(
        """
        SELECT

            route_key,
            origin_code,
            destination_code,
            avg_distance

        FROM dim_route

        ORDER BY route_key DESC

        LIMIT 100
        """
    ).fetchall()

    return {
        "data": data
    }

# =====================================================
# CREATE ROUTE
# =====================================================

@router.post("/routes")

def create_route(route: RouteCreate):

    next_id = conn.execute(
        """
        SELECT COALESCE(MAX(route_key),0)+1
        FROM dim_route
        """
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO dim_route (

            route_key,
            origin_code,
            destination_code,
            avg_distance

        )

        VALUES (?, ?, ?, ?)
        """,
        [

            next_id,
            route.origin_code,
            route.destination_code,
            route.avg_distance

        ]
    )

    return {
        "message": "Route created successfully"
    }

# =====================================================
# DELETE ROUTE
# =====================================================

@router.delete("/routes/{route_key}")

def delete_route(route_key: int):

    conn.execute(
        """
        DELETE FROM dim_route
        WHERE route_key = ?
        """,
        [route_key]
    )

    return {
        "message": "Route deleted successfully"
    }