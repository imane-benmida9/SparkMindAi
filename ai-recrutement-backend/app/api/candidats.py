"""
API Candidats : profil et CVs du candidat connecté.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.cv import CV
from app.services.auth_service import get_candidat_by_user_id


router = APIRouter(prefix="/candidats", tags=["Candidats"])


class CandidatUpdate(BaseModel):
    nom: str | None = None
    telephone: str | None = None
    localisation: str | None = None


def _cv_to_response(cv: CV) -> dict:
    return {
        "id": cv.id,
        "candidat_id": cv.candidat_id,
        "nom_fichier": cv.fichier_nom,
        "texte_brut": cv.texte_brut,
        "extracted_data": cv.json_structure,
        "json_structure": cv.json_structure,
        "date_upload": cv.date_upload.isoformat() if cv.date_upload else "",
    }


# ---------- Profil candidat (me) ----------
@router.get("/me", response_model=dict)
def me_candidat(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Profil du candidat connecté."""
    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil candidat introuvable")
    return {
        "id": candidat.id,
        "user_id": candidat.user_id,
        "nom": candidat.nom,
        "telephone": candidat.telephone,
        "localisation": candidat.localisation,
        "date_naissance": str(candidat.date_naissance) if candidat.date_naissance else None,
    }


@router.patch("/me", response_model=dict)
def update_me_candidat(
    body: CandidatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Met à jour le profil du candidat connecté."""
    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil candidat introuvable")
    if body.nom is not None:
        candidat.nom = body.nom[:255]
    if body.telephone is not None:
        candidat.telephone = body.telephone[:20] if body.telephone else None
    if body.localisation is not None:
        candidat.localisation = body.localisation[:255] if body.localisation else None
    db.commit()
    db.refresh(candidat)
    return {
        "id": candidat.id,
        "user_id": candidat.user_id,
        "nom": candidat.nom,
        "telephone": candidat.telephone,
        "localisation": candidat.localisation,
        "date_naissance": str(candidat.date_naissance) if candidat.date_naissance else None,
    }


# ---------- Liste des CVs du candidat (me ou par id pour compat frontend) ----------
@router.get("/me/cvs", response_model=list)
def my_cvs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Liste des CVs du candidat connecté. Alias de GET /cvs/my-cvs."""
    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil candidat introuvable")
    cvs = db.query(CV).filter(CV.candidat_id == candidat.id).order_by(CV.date_upload.desc()).all()
    return [_cv_to_response(c) for c in cvs]


@router.get("/{candidat_id}/cvs", response_model=list)
def get_candidat_cvs(
    candidat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste des CVs d'un candidat. Candidat : uniquement les siens (candidat_id = me)."""
    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil candidat introuvable")
    if candidat_id not in (candidat.id, "me", "current"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    cvs = db.query(CV).filter(CV.candidat_id == candidat.id).order_by(CV.date_upload.desc()).all()
    return [_cv_to_response(c) for c in cvs]
