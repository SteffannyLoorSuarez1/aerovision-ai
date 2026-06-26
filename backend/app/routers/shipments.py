from fastapi import APIRouter, Query

from app.schemas.shipment import (
    ShipmentCreateRequest,
    ShipmentCancelRequest,
)
from app.services.shipment_service import (
    create_shipment_request,
    get_my_shipments,
    cancel_shipment_request,
)

router = APIRouter(tags=["Shipments"])


@router.post("/", status_code=201)
def create_shipment(data: ShipmentCreateRequest):
    request_id = create_shipment_request(
        client_id=data.client_id,
        origin=data.origin,
        destination=data.destination,
        cargo_type=data.cargo_type,
        weight_kg=data.weight_kg,
        request_date=data.request_date,
    )
    return {"message": "Solicitud de envío creada exitosamente", "request_id": request_id}


@router.get("/my")
def get_my_shipments_endpoint(client_id: int = Query(...)):
    return {"data": get_my_shipments(client_id)}


@router.put("/{request_id}/cancel")
def cancel_shipment_endpoint(request_id: int, data: ShipmentCancelRequest):
    cancel_shipment_request(request_id=request_id, client_id=data.client_id)
    return {"message": "Solicitud cancelada exitosamente"}
