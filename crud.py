from datetime import datetime

from sqlalchemy.orm import Session

import schemas
import models


def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(models.FlightTickets).filter(models.FlightTickets.id == ticket_id).first()


def get_ticket_by_token(db: Session, booking_token: str):
    return db.query(models.FlightTickets).filter(models.FlightTickets.booking_token == booking_token).first()


def get_ticket_by_date_and_loc(db: Session, ticket: schemas.FlightBase):
    curr_model = models.FlightTickets
    return db.query(curr_model).filter(curr_model.fly_from == ticket.fly_from,
                                       curr_model.fly_to == ticket.fly_to,
                                       curr_model.dep_date == ticket.dep_date).first()


def get_ticket_calendar(db: Session, ticket: schemas.FlightBase):
    curr_model = models.FlightTickets
    return db.query(curr_model).filter(curr_model.fly_from == ticket.fly_from,
                                       curr_model.fly_to == ticket.fly_to,
                                       curr_model.dep_date >= ticket.dep_date).all()


def upsert_ticket(db: Session, ticket: schemas.FlightWrite):
    queried_ticket = get_ticket_by_date_and_loc(db, ticket)

    if not queried_ticket:

        queried_ticket = models.FlightTickets(price=ticket.price, fly_from=ticket.fly_from, fly_to=ticket.fly_to,
                                              booking_token=ticket.booking_token,
                                              dep_date=ticket.dep_date)
    else:
        queried_ticket.booking_token = ticket.booking_token
        queried_ticket.price = ticket.price
        queried_ticket.updated_at = datetime.utcnow()

    db.add(queried_ticket)
