from sqlalchemy import Float, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from datetime import datetime
from sqlalchemy import create_engine
from flask_login import UserMixin

engine = create_engine("sqlite:///skills.db")
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    ingredients: Mapped[str] = mapped_column(String(200), nullable=True)
    weight: Mapped[int] = mapped_column(Integer, nullable=True)


class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    place: Mapped[str] = mapped_column(String(100), nullable=False)
    booking_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, default=2)
    status: Mapped[str] = mapped_column(String(30), default="Очікує підтвердження")
    comment: Mapped[str] = mapped_column(String(200), default="")


Base.metadata.create_all(bind=engine)