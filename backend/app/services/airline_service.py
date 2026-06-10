from app.repositories.airline_repository import (
    get_airlines,
    create_airline
)


def list_airlines():
    return get_airlines()


def add_airline(data):

    create_airline(
        data.reporting_airline,
        data.dot_id,
        data.iata_code
    )