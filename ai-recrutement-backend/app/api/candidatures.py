"""
API Candidatures : postuler, lister, détail.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.candidature import Candidature
from app.models.cv import CV
from app.models.offre_emploi import OffreEmploi
from app.services.auth_service import get_candidat_by_user_id, get_recruteur_by_user_id
from app.ai.moteur_matching import executer_matching


router = APIRouter(prefix="/candidatures", tags=["Candidatures"])


class CandidatureCreate(BaseModel):
    offre_id: str = Field(..., description="ID de l'offre")
    cv_id: str = Field(..., description="ID du CV utilisé pour la candidature")


class CandidatureStatutUpdate(BaseModel):
    statut: str = Field(..., description="Nouveau statut: pending, interview, accepted, rejected")


def _candidature_to_response(c: Candidature) -> dict:
    return {
        "id": c.id,
        "candidat_id": c.candidat_id,
        "offre_id": c.offre_id,
        "statut": c.statut,
        "score_matching": float(c.score_matching) if c.score_matching is not None else None,
        "explication": c.explication,
        "date_candidature": c.date_candidature.isoformat() if c.date_candidature else "",
    }


# ---------- Créer une candidature (candidat) ----------
@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_candidature(
    body: CandidatureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Postuler à une offre avec un CV. Calcule le score de matching et l'explication IA."""
    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil candidat introuvable")

    cv = db.query(CV).filter(CV.id == body.cv_id).first()
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV introuvable")
    if cv.candidat_id != candidat.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CV non autorisé")

    offre = db.query(OffreEmploi).filter(OffreEmploi.id == body.offre_id).first()
    if not offre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")
    if offre.statut != "ouverte":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offre non ouverte aux candidatures")

    existing = db.query(Candidature).filter(
        Candidature.candidat_id == candidat.id,
        Candidature.offre_id == body.offre_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Candidature déjà déposée pour cette offre")

    cv_json = cv.json_structure or {}
    offre_json = offre.json_structure or {"titre": offre.titre, "description": offre.description, "competences_requises": []}

    try:
        resultat = executer_matching(cv_json, offre_json, cv_embedding=None, offre_embedding=None, generer_explications=True)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur matching : {str(e)}")

    explication_text = None
    if resultat.get("explications"):
        ex = resultat["explications"]
        if isinstance(ex, dict):
            rec = ex.get("pour_recruteur", {})
            cand = ex.get("pour_candidat", {})
            explication_text = f"Recruteur: {rec.get('synthese', '')} | Candidat: {cand.get('message_principal', '')}"
        elif hasattr(ex, "pour_recruteur"):
            explication_text = getattr(ex.pour_recruteur, "synthese", "") or getattr(ex.pour_candidat, "message_principal", "")

    candidature = Candidature(
        id=str(uuid.uuid4()),
        candidat_id=candidat.id,
        offre_id=body.offre_id,
        statut="pending",
        score_matching=resultat.get("score_final"),
        explication=explication_text,
    )
    db.add(candidature)
    db.commit()
    db.refresh(candidature)

    return _candidature_to_response(candidature)


# ---------- Liste des candidatures ----------
@router.get("", response_model=list)
def list_candidatures(
    offre_id: str | None = Query(None, description="Filtrer par offre (recruteur)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Candidat : mes candidatures. Recruteur : candidatures pour une offre (offre_id requis)."""
    if current_user.role.value == "candidat":
        candidat = get_candidat_by_user_id(db, current_user.id)
        if not candidat:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil candidat introuvable")
        q = db.query(Candidature).filter(Candidature.candidat_id == candidat.id)
    else:
        recruteur = get_recruteur_by_user_id(db, current_user.id)
        if not recruteur:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil recruteur introuvable")
        if not offre_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="offre_id requis pour le recruteur")
        # Offres du recruteur uniquement
        offres_ids = [str(o.id) for o in db.query(OffreEmploi).filter(OffreEmploi.recruteur_id == recruteur.id).all()]
        if offre_id not in offres_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Offre non autorisée")
        q = db.query(Candidature).filter(Candidature.offre_id == offre_id)
    q = q.order_by(Candidature.date_candidature.desc())
    candidatures = q.all()
    return [_candidature_to_response(c) for c in candidatures]


# ---------- Détail d'une candidature ----------
@router.get("/{candidature_id}", response_model=dict)
def get_candidature(
    candidature_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Détail d'une candidature (candidat : les siennes, recruteur : celles de ses offres)."""
    c = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable")

    if current_user.role.value == "candidat":
        candidat = get_candidat_by_user_id(db, current_user.id)
        if not candidat or c.candidat_id != candidat.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    else:
        offre = db.query(OffreEmploi).filter(OffreEmploi.id == c.offre_id).first()
        recruteur = get_recruteur_by_user_id(db, current_user.id)
        if not recruteur or not offre or offre.recruteur_id != recruteur.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")

    return _candidature_to_response(c)


# ---------- Changer le statut d'une candidature (recruteur) ----------
@router.patch("/{candidature_id}/statut", response_model=dict)
def update_candidature_statut(
    candidature_id: str,
    body: CandidatureStatutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("recruteur")),
):
    """Change le statut d'une candidature (recruteur uniquement)."""
    valid_statuts = ["pending", "interview", "accepted", "rejected"]
    if body.statut not in valid_statuts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide. Valeurs autorisées: {', '.join(valid_statuts)}"
        )
    
    candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    if not candidature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature introuvable"
        )
    
    offre = db.query(OffreEmploi).filter(OffreEmploi.id == candidature.offre_id).first()
    recruteur = get_recruteur_by_user_id(db, current_user.id)
    
    if not recruteur or not offre or offre.recruteur_id != recruteur.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier cette candidature"
        )
    
    candidature.statut = body.statut
    db.commit()
    db.refresh(candidature)
    
    return _candidature_to_response(candidature)