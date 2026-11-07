from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, relationship
from werkzeug.security import generate_password_hash

from app import db, login_manager


# Static signatures below leave SQLAlchemy's runtime constructors unchanged.
class User(UserMixin, db.Model):
    __tablename__: ClassVar[str] = "user"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    username: Mapped[str] = db.Column(db.String(180), unique=True, nullable=False)
    roles: Mapped[list[str]] = db.Column(db.JSON, nullable=False, default=list)
    password: Mapped[str] = db.Column(db.String(255), nullable=False)
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="user", cascade="all, delete-orphan"
    )

    if TYPE_CHECKING:
        def __init__(
            self,
            *,
            id: int = ...,
            username: str = ...,
            roles: list[str] = ...,
            password: str = ...,
            entries: list["Entry"] = ...,
            tasks: list["Task"] = ...,
        ) -> None: ...

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def __str__(self):
        return self.username


class Entry(db.Model):
    __tablename__: ClassVar[str] = "entry"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    user_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    entry_date: Mapped[datetime] = db.Column(db.DateTime, nullable=False)
    price: Mapped[Decimal] = db.Column(db.Numeric(10, 2), nullable=False)
    payee: Mapped[str | None] = db.Column(db.String(255))
    category: Mapped[str | None] = db.Column(db.String(255))
    notes: Mapped[str | None] = db.Column(db.Text)
    user: Mapped[User] = relationship("User", back_populates="entries")

    if TYPE_CHECKING:
        def __init__(
            self,
            *,
            id: int = ...,
            user_id: int = ...,
            entry_date: datetime = ...,
            price: Decimal = ...,
            payee: str | None = ...,
            category: str | None = ...,
            notes: str | None = ...,
            user: User = ...,
        ) -> None: ...


class Task(db.Model):
    __tablename__: ClassVar[str] = "task"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    user_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    goal: Mapped[str] = db.Column(db.String(255), nullable=False)
    reward: Mapped[str] = db.Column(db.String(255), nullable=False)
    days: Mapped[list[str]] = db.Column(db.JSON, nullable=False, default=list)
    complete: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=False)
    user: Mapped[User] = relationship("User", back_populates="tasks")

    if TYPE_CHECKING:
        def __init__(
            self,
            *,
            id: int = ...,
            user_id: int = ...,
            goal: str = ...,
            reward: str = ...,
            days: list[str] = ...,
            complete: bool = ...,
            user: User = ...,
        ) -> None: ...


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
