import uuid
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class RoleEnum(str, enum.Enum):
    candidat = "candidat"
    recruteur = "recruteur"


class User(Base):
    __tablename__ = "utilisateurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe = Column(String(255), nullable=False)  # hash bcrypt
    role = Column(SQLEnum(RoleEnum), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"