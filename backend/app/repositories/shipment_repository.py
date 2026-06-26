from app.core.database import conn
from datetime import date


def create_shipment(
    client_id: int,
    origin: str,
    destination: str,
    cargo_type: str,
    weight_kg: float,
    request_date: date,
) -> int:
    new_id = conn.execute(
        "SELECT COALESCE(MAX(request_id), 0) + 1 FROM fact_shipment_request"
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO fact_shipment_request
        (request_id, client_id, origin, destination, cargo_type, weight_kg, request_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente')
        """,
        [new_id, client_id, origin, destination, cargo_type, weight_kg, request_date]
    )

    return new_id


def get_shipments_by_client(client_id: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT request_id, origin, destination, cargo_type, weight_kg, request_date, status
        FROM fact_shipment_request
        WHERE client_id = ?
        ORDER BY request_id DESC
        """,
        [client_id]
    ).fetchall()

    return [
        {
            'request_id':   row[0],
            'origin':       row[1],
            'destination':  row[2],
            'cargo_type':   row[3],
            'weight_kg':    row[4],
            'request_date': row[5],
            'status':       row[6],
        }
        for row in rows
    ]


def get_all_shipments(status: str | None = None) -> list[dict]:
    query = """
        SELECT
            s.request_id,
            s.client_id,
            COALESCE(u.nombre, '[Usuario eliminado]') AS client_name,
            COALESCE(u.email, '[sin email]') AS client_email,
            s.origin,
            s.destination,
            s.cargo_type,
            s.weight_kg,
            s.request_date,
            s.status,
            CAST(s.created_at AS VARCHAR) AS created_at
        FROM fact_shipment_request s
        LEFT JOIN dim_users u ON s.client_id = u.id
    """
    params = []

    if status is not None:
        query += " WHERE s.status = ?"
        params.append(status)

    query += " ORDER BY s.request_id DESC"

    rows = conn.execute(query, params).fetchall()

    return [
        {
            'request_id':   row[0],
            'client_id':    row[1],
            'client_name':  row[2],
            'client_email': row[3],
            'origin':       row[4],
            'destination':  row[5],
            'cargo_type':   row[6],
            'weight_kg':    row[7],
            'request_date': row[8],
            'status':       row[9],
            'created_at':   row[10],
        }
        for row in rows
    ]


def get_shipment_by_id(request_id: int) -> dict | None:
    row = conn.execute(
        """
        SELECT request_id, client_id, origin, destination, cargo_type, weight_kg, request_date, status
        FROM fact_shipment_request
        WHERE request_id = ?
        """,
        [request_id]
    ).fetchone()

    if row is None:
        return None

    return {
        'request_id':   row[0],
        'client_id':    row[1],
        'origin':       row[2],
        'destination':  row[3],
        'cargo_type':   row[4],
        'weight_kg':    row[5],
        'request_date': row[6],
        'status':       row[7],
    }


def cancel_shipment(request_id: int) -> None:
    conn.execute(
        """
        UPDATE fact_shipment_request
        SET    status = 'Cancelado'
        WHERE  request_id = ?
        """,
        [request_id]
    )
