from fastapi import APIRouter
from app.core.database import conn

router = APIRouter()

@router.get("/operations/routes")
def get_operations_routes():

    query = """

    SELECT

        r.Origin,
        r.Dest,

        g1.latitude AS origin_lat,
        g1.longitude AS origin_lon,

        g2.latitude AS dest_lat,
        g2.longitude AS dest_lon,

        r.flights,
        r.avg_delay

    FROM fact_routes r

    JOIN dim_airport_geo g1
        ON r.Origin = g1.airport_code

    JOIN dim_airport_geo g2
        ON r.Dest = g2.airport_code

    ORDER BY r.flights DESC

    LIMIT 200

    """

    data = conn.execute(query).fetchdf()

    return {
        "data":
            data.to_dict(
                orient="records"
            )
    }