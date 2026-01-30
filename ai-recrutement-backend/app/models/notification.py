from sqlalchemy import String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID
    user_id: Mapped[str] = mapped_column(String(255), ForeignKey("utilisateurs.id"), nullable=False)
    type_notification: Mapped[str] = mapped_column(String(100), nullable=False)  # candidature_acceptée, rejet, entretien, offre_recomp, etc.
    titre: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    lien_reference: Mapped[str] = mapped_column(String(500), nullable=True)  # Lien vers la ressource (candidature, offre, etc.)
    reference_id: Mapped[str] = mapped_column(String(255), nullable=True)  # ID de la candidature/offre référencée
    lu: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    date_creation: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_lecture: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=True)
