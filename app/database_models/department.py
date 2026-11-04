from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


user_departments = Table(
    "user_departments",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "department_code",
        ForeignKey("departments.code", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Department(Base):
    __tablename__ = "departments"

    code: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    users = relationship(
        "User",
        secondary=user_departments,
        back_populates="departments",
    )
