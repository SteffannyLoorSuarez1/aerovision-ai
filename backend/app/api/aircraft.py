from fastapi import APIRouter
from pydantic import BaseModel
import duckdb

router = APIRouter()

DATABASE_PATH = "data-warehouse/warehouse.duckdb"

# =====================================================
# CONNECTION
# =====================================================

def get_connection():

    return duckdb.connect(
        DATABASE_PATH,
        read_only=False
    )

# =====================================================
# MODEL
# =====================================================

class AircraftCreate(BaseModel):

    tail_number: str
    aircraft_type: str
    manufacturer: str
    status: str

# =====================================================
# GET AIRCRAFT
# =====================================================

@router.get('/')

def get_aircraft():

    conn = get_connection()

    data = conn.execute(
        """
        SELECT

            aircraft_key,
            tail_number,
            aircraft_type,
            manufacturer,
            status

        FROM dim_aircraft

        ORDER BY aircraft_key DESC

        LIMIT 100
        """
    ).fetchall()

    conn.close()

    return {
        "data": data
    }

# =====================================================
# CREATE AIRCRAFT
# =====================================================

@router.post('/')

def create_aircraft(aircraft: AircraftCreate):

    conn = get_connection()

    next_id = conn.execute(
        """
        SELECT COALESCE(
            MAX(aircraft_key),
            0
        ) + 1
        FROM dim_aircraft
        """
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO dim_aircraft (

            aircraft_key,
            tail_number,
            aircraft_type,
            manufacturer,
            status

        )

        VALUES (?, ?, ?, ?, ?)
        """,
        [

            next_id,
            aircraft.tail_number,
            aircraft.aircraft_type,
            aircraft.manufacturer,
            aircraft.status

        ]
    )

    conn.commit()

    conn.close()

    return {
        "message": "Aircraft created successfully"
    }

# =====================================================
# DELETE AIRCRAFT
# =====================================================

@router.delete('/{aircraft_key}')

def delete_aircraft(aircraft_key: int):

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM dim_aircraft
        WHERE aircraft_key = ?
        """,
        [aircraft_key]
    )

    conn.commit()

    conn.close()

    return {
        "message": "Aircraft deleted successfully"
    }