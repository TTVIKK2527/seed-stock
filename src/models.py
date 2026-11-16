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
