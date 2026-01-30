from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Recruteur(Base):
    """Modèle Recruteur aligné sur schema.sql (recruteurs)."""
    __tablename__ = "recruteurs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, unique=True)
    entreprise: Mapped[str] = mapped_column(String(255), nullable=False)
    poste: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(20), nullable=True)
