import datetime

from sqlalchemy import Column, Integer, String, DateTime, Date

from database import Base


class FlightTickets(Base):
    __tablename__ = 'flight_tickets'

    id = Column(Integer, primary_key=True, index=True)
    fly_from = Column(String(3))
    fly_to = Column(String(3))
    dep_date = Column(Date)
    price = Column(Integer)
    booking_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
