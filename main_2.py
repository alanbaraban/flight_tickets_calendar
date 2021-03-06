from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from kiwi import get_cheapest_flights, check_flight_ticket

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
flight_destinations = [('ALA', 'TSE'), ('TSE', 'ALA'), ('ALA', 'MOW'), ('MOW', 'ALA'), ('ALA', 'CIT'),
                       ('CIT', 'ALA'), ('TSE', 'MOW'), ('MOW', 'TSE'), ('TSE', 'LED'), ('LED', 'TSE')]


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Populates the database with tickets on app launch"""
    update_tickets(flight_destinations)


@app.get("/")
def read_root():
    """Basic home endpoint"""
    return {}


@app.get("/ticket/", response_model=schemas.FlightTicket)
def get_ticket_by_date_and_loc(fly_from: str, fly_to: str, dep_date: date, db: Session = Depends(get_db)):
    """GET method, returns a ticket based on the departure date and locations; if the ticket doesn't exist in the db,
    requests the ticket from kiwi.api and inserts into db """
    ticket_base = schemas.FlightBase(fly_to=fly_to, fly_from=fly_from, dep_date=dep_date)
    ticket = crud.get_ticket_by_date_and_loc(db=db, ticket=ticket_base)
    if not ticket:
        update_tickets([(fly_from, fly_to)], fly_date=dep_date)
        ticket_base = schemas.FlightBase(fly_from=fly_from, fly_to=fly_to, dep_date=dep_date)
        ticket = crud.get_ticket_by_date_and_loc(db=db, ticket=ticket_base)
    return ticket


@app.get("/ticket/{booking_token}", response_model=schemas.FlightTicket)
def get_ticket_by_token(booking_token: str, db: Session = Depends(get_db)):
    """GET method, returns a ticket based on booking token from db"""
    ticket = crud.get_ticket_by_token(db=db, booking_token=booking_token)
    return ticket


@app.get("/verify_ticket/{booking_token}")
def verify_ticket(booking_token: str, db: Session = Depends(get_db)):
    """GET method, returns the info about the ticket's validity, if the price changes, changes the price in db"""
    ticket = check_flight_ticket(booking_token=booking_token)
    if ticket['is_price_changed'] and not ticket['is_invalid']:
        flight_ticket = crud.get_ticket_by_token(db=db, booking_token=booking_token)
        crud.upsert_ticket(db=db, ticket=flight_ticket)
        db.commit()
    return ticket


@app.get("/ticket_calendar/", response_model=List[schemas.FlightTicket])
def get_ticket_calendar(fly_from: str, fly_to: str, dep_date: date, db: Session = Depends(get_db)):
    """GET method, returns a list of dict of tickets based on location and departure date, >=dep. date"""
    ticket_base = schemas.FlightBase(fly_from=fly_from, fly_to=fly_to, dep_date=dep_date)
    tickets = crud.get_ticket_calendar(db=db, ticket=ticket_base)
    return tickets


@app.post("/cron_update_tickets/", status_code=201)
def update_data():
    """POST method, a cron method to update existing tickets"""
    update_tickets(flight_destinations)


def update_tickets(flight_routes, fly_date=None):
    """Auxiliary method, requests the tickets information and upserts them into db"""
    db = SessionLocal()
    for flight in flight_routes:
        dict_flights = get_cheapest_flights(flight[0], flight[1], fly_date)
        for key in dict_flights:
            curr_price, booking_token, fly_from, fly_to, dep_date = dict_flights[key]

            flight_ticket = schemas.FlightWrite(price=curr_price, booking_token=booking_token, fly_from=fly_from,
                                                fly_to=fly_to,
                                                dep_date=dep_date)
            crud.upsert_ticket(db=db, ticket=flight_ticket)
    db.commit()
    db.close()
