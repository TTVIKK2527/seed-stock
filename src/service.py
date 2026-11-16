from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Seed, Reservation


def seed_data(seed):
    return {"id": seed.id, "name": seed.name, "quantity": seed.quantity, "createdAt": seed.created_at}


def reservation_data(reservation):
    return {"id": reservation.id, "seedId": reservation.seed_id, "quantity": reservation.quantity,
            "status": reservation.status, "createdAt": reservation.created_at}


def validate_quantity(quantity, positive=False):
    if type(quantity) is not int or quantity < (1 if positive else 0):
        raise ValueError("Kogus peab olema " + ("positiivne" if positive else "mittenegatiivne") + " täisarv.")


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
                if session.get(Seed, seed_id) is None: raise ValueError("Seemet ei leitud.")
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
