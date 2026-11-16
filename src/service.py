from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Seed, Reservation


def seed_data(seed):
    return {"id": seed.id, "name": seed.name, "quantity": seed.quantity, "createdAt": seed.created_at}


def reservation_data(reservation):
    data = {"id": reservation.id, "seedId": reservation.seed_id, "quantity": reservation.quantity,
            "status": reservation.status, "createdAt": reservation.created_at}
    if reservation.cancelled_at is not None: data["cancelledAt"] = reservation.cancelled_at
    return data


def validate_quantity(quantity, positive=False):
    if type(quantity) is not int or quantity < (1 if positive else 0):
        raise ValueError("Kogus peab olema " + ("positiivne" if positive else "mittenegatiivne") + " täisarv.")


def require_record(session, model, key, message):
    record = session.get(model, key)
    if record is None: raise ValueError(message)
    return record


class StockService:
    def __init__(self, engine, clock=None, id_provider=None):
        self.engine = engine
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        self.id_provider = id_provider or (lambda: str(uuid4()))

    def add_seed(self, name, quantity):
        if not isinstance(name, str) or not name.strip(): raise ValueError("Nimi peab olema täidetud.")
        validate_quantity(quantity)
        seed = Seed(id=self.id_provider(), name=name.strip(), name_key=name.strip().casefold(), quantity=quantity, created_at=self.clock())
        try:
            with Session(self.engine, expire_on_commit=False) as session, session.begin():
                session.add(seed)
                session.flush()
        except IntegrityError as error:
            raise ValueError("Sama nimi või ID on juba olemas.") from error
        return seed_data(seed)

    def list_seeds(self):
        with Session(self.engine) as session:
            return [seed_data(seed)
                    for seed in session.scalars(select(Seed).order_by(Seed.name_key, Seed.id))]

    def reserve(self, seed_id, quantity):
        validate_quantity(quantity, positive=True)
        try:
            with Session(self.engine, expire_on_commit=False) as session, session.begin():
                require_record(session, Seed, seed_id, "Seemet ei leitud.")
                result = session.execute(update(Seed).where(Seed.id == seed_id, Seed.quantity >= quantity)
                                         .values(quantity=Seed.quantity - quantity))
                if result.rowcount != 1: raise ValueError("Seemneid ei piisa.")
                reservation = Reservation(id=self.id_provider(), seed_id=seed_id, quantity=quantity, status="active", created_at=self.clock())
                session.add(reservation)
                session.flush()
        except IntegrityError as error:
            raise ValueError("Broneeringu salvestamine ebaõnnestus.") from error
        return reservation_data(reservation)

    def list_reservations(self):
        with Session(self.engine) as session:
            return [reservation_data(r)
                    for r in session.scalars(select(Reservation).order_by(Reservation.created_at, Reservation.id))]

    def cancel(self, reservation_id):
        with Session(self.engine, expire_on_commit=False) as session, session.begin():
            reservation = require_record(session, Reservation, reservation_id, "Broneeringut ei leitud.")
            now = self.clock()
            result = session.execute(update(Reservation).where(Reservation.id == reservation_id, Reservation.status == "active")
                                     .values(status="cancelled", cancelled_at=now))
            if result.rowcount != 1: raise ValueError("Broneering on juba tühistatud.")
            session.execute(update(Seed).where(Seed.id == reservation.seed_id).values(quantity=Seed.quantity + reservation.quantity))
            session.refresh(reservation)
        return reservation_data(reservation)
