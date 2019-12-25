from datetime import date, datetime

from pydantic import BaseModel


class FlightBase(BaseModel):
    fly_from: str
    fly_to: str
    dep_date: date

    class Config:
        orm_mode = True


class FlightWrite(FlightBase):
    price: int
    booking_token: str


class FlightTicket(FlightWrite):
    id: int
    created_at: datetime
    updated_at: datetime
