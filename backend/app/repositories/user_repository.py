from app.core.database import conn


def find_by_email(email: str) -> dict | None:
    row = conn.execute(
        "SELECT id, nombre, email, password_hash, rol, activo FROM dim_users WHERE email = ?",
        [email]
    ).fetchone()

    if row is None:
        return None

    return {
        'id': row[0],
        'nombre': row[1],
        'email': row[2],
        'password_hash': row[3],
        'rol': row[4],
        'activo': row[5],
    }


def create_user(nombre: str, email: str, password_hash: str) -> int:
    new_id = conn.execute(
        "SELECT nextval('users_id_seq')"
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO dim_users (id, nombre, email, password_hash, rol, activo)
        VALUES (?, ?, ?, ?, 'cliente', true)
        """,
        [new_id, nombre, email, password_hash]
    )

    return new_id
