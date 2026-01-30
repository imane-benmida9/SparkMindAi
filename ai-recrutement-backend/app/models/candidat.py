from sqlalchemy import String, DateTime, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Candidat(Base):
    """Modèle Candidat aligné sur schema.sql (candidats)."""
    __tablename__ = "candidats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, unique=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    telephone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    localisation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_naissance: Mapped[object | None] = mapped_column(Date, nullable=True)
