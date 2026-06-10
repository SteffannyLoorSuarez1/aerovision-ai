from fastapi import APIRouter
from app.core.database import conn

router = APIRouter()

# =====================================================
# TOTAL FLIGHTS
# =====================================================

@router.get('/flights/count')

def flights_count():

    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_flights
        """
    ).fetchone()[0]

    return {
        'count': count
    }

# =====================================================
# AIRLINES COUNT
# =====================================================

@router.get('/airlines/count')

def airlines_count():

    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM dim_airline
        """
    ).fetchone()[0]

    return {
        'count': count
    }

# =====================================================
# AVG DELAY
# =====================================================

@router.get('/delays/avg')

def avg_delay():

    avg_delay = conn.execute(
        """
        SELECT ROUND(
            AVG(CAST(ArrDelay AS DOUBLE)),
            2
        )
        FROM fact_flights
        WHERE ArrDelay IS NOT NULL
        """
    ).fetchone()[0]

    return {
        'avg_delay': avg_delay
    }

# =====================================================
# CANCELLED FLIGHTS
# =====================================================

@router.get('/cancelled/count')

def cancelled_count():

    count = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_flights
        WHERE Cancelled = '1.00'
        """
    ).fetchone()[0]

    return {
        'count': count
    }

# =====================================================
# KPI AIRLINES
# =====================================================

@router.get('/kpi/airlines')

def kpi_airlines():

    data = conn.execute(
        """
        SELECT

            Reporting_Airline,

            COUNT(*) AS total_flights,

            ROUND(
                AVG(CAST(ArrDelay AS DOUBLE)),
                2
            ) AS avg_delay

        FROM fact_flights

        GROUP BY Reporting_Airline

        ORDER BY total_flights DESC

        LIMIT 10
        """
    ).fetchall()

    return {
        'data': data
    }

# =====================================================
# GEO AIRPORTS
# =====================================================

@router.get('/geo/airports')

def geo_airports():

    airports = [

        {
            "code": "JFK",
            "city": "New York",
            "state": "New York",
            "lat": 40.6413,
            "lon": -73.7781
        },

        {
            "code": "LAX",
            "city": "Los Angeles",
            "state": "California",
            "lat": 33.9416,
            "lon": -118.4085
        },

        {
            "code": "ORD",
            "city": "Chicago",
            "state": "Illinois",
            "lat": 41.9742,
            "lon": -87.9073
        },

        {
            "code": "DFW",
            "city": "Dallas",
            "state": "Texas",
            "lat": 32.8998,
            "lon": -97.0403
        },

        {
            "code": "ATL",
            "city": "Atlanta",
            "state": "Georgia",
            "lat": 33.6407,
            "lon": -84.4277
        }

    ]

    return {
        "data": airports
    }
# =====================================================
# TABLES
# =====================================================

@router.get('/tables')

def tables():

    data = conn.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        ORDER BY table_name
        """
    ).fetchall()

    return {
        'data': data
    }
@router.get('/columns/{table_name}')
def table_columns(table_name: str):

    data = conn.execute(f"""
        DESCRIBE {table_name}
    """).fetchall()

    return {
        "table": table_name,
        "columns": data
    }
@router.get('/columns/{table_name}')
def table_columns(table_name: str):

    data = conn.execute(f"""
        DESCRIBE {table_name}
    """).fetchall()

    return {
        "table": table_name,
        "columns": data
    }
@router.get('/create-aircraft')
def create_aircraft_dimension():

    conn.execute("""

    CREATE OR REPLACE TABLE dim_aircraft AS

    SELECT DISTINCT

        ROW_NUMBER() OVER() AS aircraft_key,

        Tail_Number AS tail_number,

        'Unknown' AS aircraft_type,

        'Unknown' AS manufacturer,

        'ACTIVE' AS status

    FROM raw_flights

    WHERE Tail_Number IS NOT NULL

    """)

    return {
        "message": "dim_aircraft created"
    }


@router.get('/create-route')
def create_route_dimension():

    conn.execute("""

    CREATE OR REPLACE TABLE dim_route AS

    SELECT DISTINCT

        ROW_NUMBER() OVER() AS route_key,

        Origin AS origin_code,

        Dest AS destination_code,

        AVG(
            CAST(Distance AS DOUBLE)
        ) OVER (
            PARTITION BY Origin, Dest
        ) AS avg_distance

    FROM raw_flights

    WHERE
        Origin IS NOT NULL
        AND Dest IS NOT NULL

    """)

    return {
        "message": "dim_route created"
    }
# =====================================================
# TOP ROUTES KPI
# =====================================================

@router.get('/kpi/routes')

def kpi_routes():

    data = conn.execute(
        """
        SELECT

            Origin,
            Dest,

            COUNT(*) AS total_flights

        FROM fact_flights

        GROUP BY

            Origin,
            Dest

        ORDER BY total_flights DESC

        LIMIT 10
        """
    ).fetchall()

    return {
        "data": data
    }
# =====================================================
# KPI AIRPORTS
# =====================================================

@router.get('/kpi/airports')

def kpi_airports():

    data = conn.execute(
        """
        SELECT

            Origin,

            COUNT(*) AS total_flights

        FROM fact_flights

        GROUP BY Origin

        ORDER BY total_flights DESC

        LIMIT 10
        """
    ).fetchall()

    return {
        "data": data
    }
# =====================================================
# KPI PUNCTUALITY
# =====================================================

@router.get('/kpi/punctuality')

def kpi_punctuality():

    data = conn.execute(
        """
        SELECT

            Reporting_Airline,

            ROUND(
                AVG(
                    CAST(ArrDelay AS DOUBLE)
                ),
                2
            ) AS avg_delay

        FROM fact_flights

        WHERE ArrDelay IS NOT NULL

        GROUP BY Reporting_Airline

        ORDER BY avg_delay ASC

        LIMIT 10
        """
    ).fetchall()

    return {
        "data": data
    }
# =====================================================
# KPI CANCELLATIONS
# =====================================================

@router.get('/kpi/cancellations')

def kpi_cancellations():

    data = conn.execute(
        """
        SELECT

            Reporting_Airline,

            COUNT(*) AS cancelled

        FROM fact_flights

        WHERE Cancelled = '1.00'

        GROUP BY Reporting_Airline

        ORDER BY cancelled DESC

        LIMIT 10
        """
    ).fetchall()

    return {
        "data": data
    }

# =====================================================
# AI INSIGHTS
# =====================================================

@router.get('/insights')

def insights():

    top_airport = conn.execute("""
        SELECT Origin, COUNT(*) flights
        FROM fact_flights
        GROUP BY Origin
        ORDER BY flights DESC
        LIMIT 1
    """).fetchone()

    top_route = conn.execute("""
        SELECT Origin, Dest, COUNT(*) flights
        FROM fact_flights
        GROUP BY Origin, Dest
        ORDER BY flights DESC
        LIMIT 1
    """).fetchone()

    best_airline = conn.execute("""
        SELECT
            Reporting_Airline,
            AVG(CAST(ArrDelay AS DOUBLE)) avg_delay
        FROM fact_flights
        WHERE ArrDelay IS NOT NULL
        GROUP BY Reporting_Airline
        ORDER BY avg_delay ASC
        LIMIT 1
    """).fetchone()

    worst_airline = conn.execute("""
        SELECT
            Reporting_Airline,
            COUNT(*) cancelled
        FROM fact_flights
        WHERE Cancelled = '1.00'
        GROUP BY Reporting_Airline
        ORDER BY cancelled DESC
        LIMIT 1
    """).fetchone()

    return {

        "top_airport": top_airport[0],

        "top_route":
            f"{top_route[0]} → {top_route[1]}",

        "best_airline":
            best_airline[0],

        "most_cancelled_airline":
            worst_airline[0],

        "insights": [

            f"Airport with highest traffic: {top_airport[0]}",

            f"Most used route: {top_route[0]} → {top_route[1]}",

            f"Best punctual airline: {best_airline[0]}",

            f"Highest cancellations: {worst_airline[0]}"

        ]
    }