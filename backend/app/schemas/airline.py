from pydantic import BaseModel

class AirlineCreate(BaseModel):
    reporting_airline: str
    dot_id: int
    iata_code: str