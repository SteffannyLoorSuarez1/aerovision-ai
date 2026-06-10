from fastapi import APIRouter
from app.core.database import conn

import pandas as pd

router = APIRouter()

@router.get('/ai/train-model')
def train_model():

    query = """
    SELECT

        Reporting_Airline,
        Origin,
        Dest,
        Distance,
        Cancelled

    FROM fact_flights

    WHERE Distance IS NOT NULL
    """

    df = conn.execute(query).df()

    return {
        "rows": len(df)
    }