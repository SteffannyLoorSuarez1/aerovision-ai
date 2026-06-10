from fastapi import APIRouter
from app.core.database import conn

router = APIRouter()

# =====================================================
# DEBUG DIM_AIRPORT_GEO
# =====================================================

@router.get('/operations/debug')

def debug_operations():

    data = conn.execute("""

        DESCRIBE dim_airport_geo

    """).fetchall()

    return {
        'data': data
    }
