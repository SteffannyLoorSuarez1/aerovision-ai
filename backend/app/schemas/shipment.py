from pydantic import BaseModel, field_validator
from datetime import date


class ShipmentCreateRequest(BaseModel):
    client_id:    int
    origin:       str
    destination:  str
    cargo_type:   str
    weight_kg:    float
    request_date: date

    @field_validator('weight_kg')
    @classmethod
    def weight_positive(cls, v):
        if v <= 0:
            raise ValueError('El peso debe ser mayor que cero')
        return v

    @field_validator('origin', 'destination', 'cargo_type')
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('El campo no puede estar vacío')
        return v.strip()


class ShipmentCancelRequest(BaseModel):
    client_id: int


class ShipmentResponse(BaseModel):
    request_id:   int
    origin:       str
    destination:  str
    cargo_type:   str
    weight_kg:    float
    request_date: date
    status:       str


class AdminShipmentResponse(BaseModel):
    request_id:   int
    client_id:    int
    client_name:  str
    client_email: str
    origin:       str
    destination:  str
    cargo_type:   str
    weight_kg:    float
    request_date: date
    status:       str
    created_at:   str
