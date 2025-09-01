from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from sqlalchemy import Integer, String, ForeignKey
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship("User", back_populates="resumes")
