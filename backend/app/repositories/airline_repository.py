from app.core.database import get_connection


def get_airlines():

    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM dim_airline
        ORDER BY airline_key
        LIMIT 100
    """).fetchall()

    conn.close()

    return rows


def create_airline(
    reporting_airline,
    dot_id,
    iata_code
):

    conn = get_connection()

    max_id = conn.execute("""
        SELECT COALESCE(MAX(airline_key), 0)
        FROM dim_airline
    """).fetchone()[0]

    new_id = max_id + 1

    conn.execute("""
        INSERT INTO dim_airline
        VALUES (?, ?, ?, ?)
    """, (
        new_id,
        reporting_airline,
        dot_id,
        iata_code
    ))

    conn.close()