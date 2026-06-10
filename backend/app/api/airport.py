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
        DATABASE_PATH
    )

# =====================================================
# SCHEMA
# =====================================================

class AirportCreate(BaseModel):

    airport_id: str
    airport_code: str
    city_name: str
    state_name: str

# =====================================================
# GET AIRPORTS
# =====================================================

@router.get('/')

def get_airports():

    conn = get_connection()

    data = conn.execute(
        '''
        SELECT
            airport_key,
            airport_id,
            airport_code,
            city_name,
            state_name
        FROM dim_airport
        LIMIT 50
        '''
    ).fetchall()

    conn.close()

    return {
        'data': data
    }

# =====================================================
# CREATE AIRPORT
# =====================================================

@router.post('/')

def create_airport(
    airport: AirportCreate
):

    conn = get_connection()

    max_id = conn.execute(
        '''
        SELECT COALESCE(
            MAX(airport_key),
            0
        )
        FROM dim_airport
        '''
    ).fetchone()[0]

    new_id = max_id + 1

    conn.execute(
        '''
        INSERT INTO dim_airport (

            airport_key,
            airport_id,
            airport_code,
            city_name,
            state_name

        )

        VALUES (?, ?, ?, ?, ?)
        ''',
        [

            new_id,
            airport.airport_id,
            airport.airport_code,
            airport.city_name,
            airport.state_name

        ]
    )

    conn.commit()

    conn.close()

    return {
        'message': 'Airport created successfully'
    }

# =====================================================
# DELETE AIRPORT
# =====================================================

@router.delete('/{airport_key}')

def delete_airport(
    airport_key: int
):

    conn = get_connection()

    conn.execute(
        '''
        DELETE FROM dim_airport
        WHERE airport_key = ?
        ''',
        [airport_key]
    )

    conn.commit()

    conn.close()

    return {
        'message': 'Airport deleted successfully'
    }