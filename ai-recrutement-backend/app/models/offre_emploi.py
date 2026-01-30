from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base

# Statut aligné sur schema statut_offre_enum
import enum
class StatutOffreEnum(str, enum.Enum):
    ouverte = "ouverte"
    fermee = "fermee"


class OffreEmploi(Base):
    """Modèle Offre aligné sur schema.sql (offres_emploi)."""
    __tablename__ = "offres_emploi"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    recruteur_id: Mapped[str] = mapped_column(String(36), ForeignKey("recruteurs.id", ondelete="CASCADE"), nullable=False)
    titre: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    localisation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type_contrat: Mapped[str | None] = mapped_column(String(50), nullable=True)
    salaire_min: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    salaire_max: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    experience_requise: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_publication: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouverte")
    json_structure: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
