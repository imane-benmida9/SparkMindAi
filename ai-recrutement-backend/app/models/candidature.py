from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Candidature(Base):
    """Modèle Candidature aligné sur schema.sql (candidatures)."""
    __tablename__ = "candidatures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidat_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidats.id", ondelete="CASCADE"), nullable=False)
    offre_id: Mapped[str] = mapped_column(String(36), ForeignKey("offres_emploi.id", ondelete="CASCADE"), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    score_matching: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    explication: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_candidature: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
