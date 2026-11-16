from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Seed


class StockService:
    def __init__(self, engine, clock=None, id_provider=None):
        self.engine = engine
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        self.id_provider = id_provider or (lambda: str(uuid4()))

    def add_seed(self, name, quantity):
        if not isinstance(name, str) or not name.strip(): raise ValueError("Nimi peab olema täidetud.")
        if type(quantity) is not int or quantity < 0: raise ValueError("Kogus peab olema mittenegatiivne täisarv.")
        seed = Seed(id=self.id_provider(), name=name.strip(), name_key=name.strip().casefold(), quantity=quantity, created_at=self.clock())
        try:
            with Session(self.engine, expire_on_commit=False) as session, session.begin():
                session.add(seed)
                session.flush()
        except IntegrityError as error:
            raise ValueError("Sama nimi või ID on juba olemas.") from error
        return {"id": seed.id, "name": seed.name, "quantity": seed.quantity, "createdAt": seed.created_at}

    def list_seeds(self):
        with Session(self.engine) as session:
            return [{"id": seed.id, "name": seed.name, "quantity": seed.quantity, "createdAt": seed.created_at}
                    for seed in session.scalars(select(Seed).order_by(Seed.name_key, Seed.id))]
