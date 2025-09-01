from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from sqlalchemy import Integer, String
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .resume import Resume


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)

    resumes: Mapped[List["Resume"]] = relationship("Resume", back_populates="owner")
