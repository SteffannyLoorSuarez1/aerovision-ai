from fastapi import APIRouter
from pydantic import BaseModel
import duckdb

router = APIRouter()

DATABASE_PATH = "data-warehouse/warehouse.duckdb"
# =====================================================
# MODEL
# =====================================================

class AirlineCreate(BaseModel):

    reporting_airline: str
    dot_id: int
    iata_code: str

# =====================================================
# GET CONNECTION
# =====================================================

def get_connection():

    return duckdb.connect(
        DATABASE_PATH,
        read_only=False
    )

# =====================================================
# GET AIRLINES
# =====================================================

@router.get('/')

def get_airlines():

    conn = get_connection()

    data = conn.execute(
        """
        SELECT

            airline_key,
            Reporting_Airline,
            DOT_ID_Reporting_Airline,
            IATA_CODE_Reporting_Airline

        FROM dim_airline

        ORDER BY airline_key

        LIMIT 100
        """
    ).fetchall()

    conn.close()

    return {
        'data': data
    }

# =====================================================
# CREATE AIRLINE
# =====================================================

@router.post('/')

def create_airline(airline: AirlineCreate):

    conn = get_connection()

    next_id = conn.execute(
        """
        SELECT COALESCE(MAX(airline_key),0)+1
        FROM dim_airline
        """
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO dim_airline (

            airline_key,
            Reporting_Airline,
            DOT_ID_Reporting_Airline,
            IATA_CODE_Reporting_Airline

        )

        VALUES (?, ?, ?, ?)
        """,
        [

            next_id,
            airline.reporting_airline,
            str(airline.dot_id),
            airline.iata_code

        ]
    )

    conn.commit()

    conn.close()

    return {
        'message': 'Airline created successfully'
    }

# =====================================================
# DELETE AIRLINE
# =====================================================

@router.delete('/{airline_key}')

def delete_airline(airline_key: int):

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM dim_airline
        WHERE airline_key = ?
        """,
        [airline_key]
    )

    conn.commit()

    conn.close()

    return {
        'message': 'Airline deleted successfully'
    }