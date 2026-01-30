from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class CV(Base):
    """Modèle CV aligné sur schema.sql (cvs)."""
    __tablename__ = "cvs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidat_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidats.id", ondelete="CASCADE"), nullable=False)
    fichier_nom: Mapped[str] = mapped_column(String(255), nullable=False)
    texte_brut: Mapped[str | None] = mapped_column(Text, nullable=True)
    json_structure: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    date_upload: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
