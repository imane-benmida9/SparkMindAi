import enum
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class RoleEnum(str, enum.Enum):
    candidat = "candidat"
    recruteur = "recruteur"


class User(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID en string pour MVP
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    mot_de_passe: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name="role_enum"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    date_creation: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
