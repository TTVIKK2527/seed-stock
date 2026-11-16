from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): pass


class Seed(Base):
    __tablename__ = "seeds"
    __table_args__ = (CheckConstraint("quantity >= 0"),)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    name_key: Mapped[str] = mapped_column(String, unique=True)
    quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(String)


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (CheckConstraint("quantity > 0"), CheckConstraint("status IN ('active', 'cancelled')"))
    id: Mapped[str] = mapped_column(String, primary_key=True)
    seed_id: Mapped[str] = mapped_column(ForeignKey("seeds.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String)
    cancelled_at: Mapped[str | None] = mapped_column(String, nullable=True)
