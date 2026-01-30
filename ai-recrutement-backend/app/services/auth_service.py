from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from app.models.user import User, RoleEnum
from app.models.candidat import Candidat
from app.models.recruteur import Recruteur
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalars().first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.execute(select(User).where(User.id == user_id)).scalars().first()


def get_candidat_by_user_id(db: Session, user_id: str) -> Candidat | None:
    return db.execute(select(Candidat).where(Candidat.user_id == user_id)).scalars().first()


def get_recruteur_by_user_id(db: Session, user_id: str) -> Recruteur | None:
    return db.execute(select(Recruteur).where(Recruteur.user_id == user_id)).scalars().first()


def create_user(db: Session, email: str, password: str, role: str, nom: str | None = None) -> User:
    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        mot_de_passe=hash_password(password),
        role=RoleEnum(role),
        is_active=True,
    )
    db.add(user)
    db.flush()

    if role == "candidat":
        nom_candidat = (nom or email.split("@")[0] or "Candidat").strip()[:255]
        candidat = Candidat(id=str(uuid.uuid4()), user_id=user_id, nom=nom_candidat)
        db.add(candidat)
    elif role == "recruteur":
        entreprise = (nom or "Mon entreprise").strip()[:255]
        recruteur = Recruteur(id=str(uuid.uuid4()), user_id=user_id, entreprise=entreprise)
        db.add(recruteur)

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.mot_de_passe):
        return None
    return user
