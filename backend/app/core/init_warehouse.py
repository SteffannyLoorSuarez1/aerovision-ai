import duckdb

# =====================================================
# DATABASE PATH
# =====================================================

DATABASE_PATH = "data-warehouse/warehouse.duckdb"
# =====================================================
# CSV DATASET
# =====================================================

CSV_PATH = "/datasets/airline_2m.csv"
# =====================================================
# CONNECTION
# =====================================================
conn = duckdb.connect(
    DATABASE_PATH,
    read_only=False
)
# =====================================================
# RAW TABLE
# =====================================================

print("Creating RAW table...")

conn.execute(f"""
CREATE OR REPLACE TABLE raw_flights AS

SELECT *

FROM read_csv_auto(

    '{CSV_PATH}',

    ignore_errors=true,
    all_varchar=true

)
""")

print("RAW table created.")

# =====================================================
# STAGING AIRLINES
# =====================================================

print("Creating stg_airlines...")

conn.execute("""

CREATE OR REPLACE TABLE stg_airlines AS

SELECT DISTINCT

    Reporting_Airline,
    DOT_ID_Reporting_Airline,
    IATA_CODE_Reporting_Airline

FROM raw_flights

WHERE Reporting_Airline IS NOT NULL

""")

print("stg_airlines created.")

# =====================================================
# DIM AIRLINE
# =====================================================

print("Creating dim_airline...")

conn.execute("""

CREATE OR REPLACE TABLE dim_airline AS

SELECT

    ROW_NUMBER() OVER() AS airline_key,

    Reporting_Airline,
    DOT_ID_Reporting_Airline,
    IATA_CODE_Reporting_Airline

FROM stg_airlines

""")

print("dim_airline created.")

# =====================================================
# DIM AIRPORT
# =====================================================

print("Creating dim_airport...")

conn.execute("""

CREATE OR REPLACE TABLE dim_airport AS

SELECT DISTINCT

    ROW_NUMBER() OVER() AS airport_key,

    OriginAirportID AS airport_id,
    Origin AS airport_code,
    OriginCityName AS city_name,
    OriginState AS state_code,
    OriginStateName AS state_name

FROM raw_flights

WHERE Origin IS NOT NULL

""")

print("dim_airport created.")

# =====================================================
# DIM AIRPORT GEO
# =====================================================

print("Creating dim_airport_geo...")

conn.execute("""

CREATE OR REPLACE TABLE dim_airport_geo AS

SELECT *

FROM read_csv_auto(
    'data/airport_geo.csv'
)

""")

print("dim_airport_geo created.")

# =====================================================
# DIM AIRCRAFT
# =====================================================

print("Creating dim_aircraft...")

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

print("dim_aircraft created.")

# =====================================================
# DIM ROUTE
# =====================================================

print("Creating dim_route...")

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

    AND

    Dest IS NOT NULL

""")

print("dim_route created.")
# =====================================================
# DIM DATE
# =====================================================

print("Creating dim_date...")

conn.execute("""

CREATE OR REPLACE TABLE dim_date AS

SELECT DISTINCT

    ROW_NUMBER() OVER() AS date_key,

    FlightDate,
    Year,
    Quarter,
    Month,
    DayofMonth,
    DayOfWeek

FROM raw_flights

""")

print("dim_date created.")

# =====================================================
# FACT FLIGHTS
# =====================================================

print("Creating fact_flights...")

conn.execute("""

CREATE OR REPLACE TABLE fact_flights AS

SELECT

    ROW_NUMBER() OVER() AS flight_key,

    Reporting_Airline,
    Origin,
    Dest,
    FlightDate,

    DepDelay,
    ArrDelay,

    TaxiOut,
    TaxiIn,

    AirTime,
    Distance,

    Cancelled,
    Diverted,

    CarrierDelay,
    WeatherDelay,
    NASDelay,
    SecurityDelay,
    LateAircraftDelay

FROM raw_flights

""")

print("fact_flights created.")

# =====================================================
# DONE
# =====================================================
# =====================================================
# FACT AIRPORT OPERATIONS
# =====================================================

print("Creating fact_airport_operations...")

conn.execute("""

CREATE OR REPLACE TABLE fact_airport_operations AS

SELECT

    Origin AS airport_code,

    COUNT(*) AS total_flights,

    AVG(CAST(DepDelay AS DOUBLE)) AS avg_dep_delay,

    AVG(CAST(ArrDelay AS DOUBLE)) AS avg_arr_delay,

    AVG(CAST(TaxiOut AS DOUBLE)) AS avg_taxi_out,

    AVG(CAST(TaxiIn AS DOUBLE)) AS avg_taxi_in,

    SUM(CAST(Cancelled AS DOUBLE)) AS cancelled_flights,

    SUM(CAST(Diverted AS DOUBLE)) AS diverted_flights,

    AVG(CAST(WeatherDelay AS DOUBLE)) AS weather_delay,

    AVG(CAST(CarrierDelay AS DOUBLE)) AS carrier_delay,

    AVG(CAST(NASDelay AS DOUBLE)) AS nas_delay,

    AVG(CAST(LateAircraftDelay AS DOUBLE))
        AS late_aircraft_delay

FROM fact_flights

GROUP BY Origin

""")

print("fact_airport_operations created.")



# =====================================================
# FACT ROUTES
# =====================================================

print("Creating fact_routes...")

conn.execute("""

CREATE OR REPLACE TABLE fact_routes AS

SELECT

    Origin,
    Dest,

    COUNT(*) AS flights,

    AVG(
        CAST(ArrDelay AS DOUBLE)
    ) AS avg_delay

FROM fact_flights

GROUP BY

    Origin,
    Dest

""")

print("fact_routes created.")
print("Warehouse initialization completed.")

conn.close()