from datetime import date
from fastapi import HTTPException

from app.repositories.shipment_repository import (
    create_shipment,
    get_shipments_by_client,
    get_all_shipments,
    get_shipment_by_id,
    cancel_shipment,
)


def create_shipment_request(
    client_id: int,
    origin: str,
    destination: str,
    cargo_type: str,
    weight_kg: float,
    request_date: date,
) -> int:
    if origin == destination:
        raise HTTPException(
            status_code=400,
            detail="El origen y el destino no pueden ser iguales"
        )

    if request_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="La fecha de envío no puede ser en el pasado"
        )

    return create_shipment(client_id, origin, destination, cargo_type, weight_kg, request_date)


def get_my_shipments(client_id: int) -> list[dict]:
    return get_shipments_by_client(client_id)


def get_all_shipments_service(status: str | None = None) -> list[dict]:
    return get_all_shipments(status)


def cancel_shipment_request(request_id: int, client_id: int) -> None:
    shipment = get_shipment_by_id(request_id)

    if shipment is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if shipment['client_id'] != client_id:
        raise HTTPException(status_code=403, detail="No autorizado para cancelar esta solicitud")

    if shipment['status'] != 'Pendiente':
        raise HTTPException(status_code=409, detail="Solo se pueden cancelar solicitudes en estado Pendiente")

    cancel_shipment(request_id)
