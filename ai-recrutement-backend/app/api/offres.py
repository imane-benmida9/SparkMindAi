"""
API Offres : CRUD + indexation Chroma + recherche sémantique.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, require_roles
from app.models.user import User
from app.models.offre_emploi import OffreEmploi
from app.services.auth_service import get_recruteur_by_user_id
from app.vector_store.indexing import index_offer, search_cvs_for_offer


router = APIRouter(prefix="/offres", tags=["Offres"])


# ---------- Schémas ----------
class OffreCreate(BaseModel):
    titre: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    localisation: str | None = None
    type_contrat: str | None = None
    salaire_min: float | None = None
    salaire_max: float | None = None
    experience_requise: int | None = None
    competences_requises: list[str] | None = None  # pour json_structure


class OffreUpdate(BaseModel):
    titre: str | None = None
    description: str | None = None
    localisation: str | None = None
    type_contrat: str | None = None
    salaire_min: float | None = None
    salaire_max: float | None = None
    experience_requise: int | None = None
    statut: str | None = None


class OffreResponse(BaseModel):
    id: str
    recruteur_id: str
    titre: str
    description: str
    localisation: str | None
    type_contrat: str | None
    salaire_min: float | None
    salaire_max: float | None
    experience_requise: int | None
    date_publication: str
    statut: str
    json_structure: dict | None

    class Config:
        from_attributes = True


class OffreIndexRequest(BaseModel):
    offre_id: str = Field(..., description="ID de l'offre")
    offre: dict[str, Any] | str = Field(..., description="Offre (JSON ou texte)")
    metadata: dict[str, Any] | None = None


class OffreSearchCVRequest(BaseModel):
    offre: dict[str, Any] | str = Field(..., description="Offre (JSON ou texte)")
    top_k: int = Field(default=10, ge=1, le=50)


def _offre_to_response(o: OffreEmploi) -> dict:
    return {
        "id": o.id,
        "recruteur_id": o.recruteur_id,
        "titre": o.titre,
        "description": o.description,
        "localisation": o.localisation,
        "type_contrat": o.type_contrat,
        "salaire_min": float(o.salaire_min) if o.salaire_min is not None else None,
        "salaire_max": float(o.salaire_max) if o.salaire_max is not None else None,
        "experience_requise": int(o.experience_requise) if o.experience_requise is not None else None,
        "date_publication": o.date_publication.isoformat() if o.date_publication else "",
        "statut": o.statut,
        "json_structure": o.json_structure,
        "competences_requises": (",".join(o.json_structure.get("competences_requises", [])) if o.json_structure and isinstance(o.json_structure.get("competences_requises"), list) else None),
        "niveau_etude": o.json_structure.get("niveau_etude") if o.json_structure else None,
    }


def _build_offre_json(body: OffreCreate) -> dict:
    return {
        "titre": body.titre,
        "description": body.description,
        "localisation": body.localisation or "",
        "type_contrat": body.type_contrat or "",
        "competences_requises": body.competences_requises or [],
    }


# ---------- Liste des offres (pagination, filtre statut) ----------
@router.get("", response_model=list)
def list_offres(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    statut: str | None = Query(None, description="ouverte | fermee"),
    localisation: str | None = Query(None),
    mine: bool = Query(False, description="Si true et recruteur connecté: uniquement ses offres"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Liste les offres avec pagination. Filtre par statut (ouverte par défaut), localisation. mine=true: offres du recruteur connecté."""
    q = db.query(OffreEmploi)
    if mine and current_user and current_user.role.value == "recruteur":
        recruteur = get_recruteur_by_user_id(db, current_user.id)
        if recruteur:
            q = q.filter(OffreEmploi.recruteur_id == recruteur.id)
    if statut:
        q = q.filter(OffreEmploi.statut == statut)
    else:
        q = q.filter(OffreEmploi.statut == "ouverte")
    if localisation:
        q = q.filter(OffreEmploi.localisation.ilike(f"%{localisation}%"))
    q = q.order_by(OffreEmploi.date_publication.desc())
    offres = q.offset((page - 1) * limit).limit(limit).all()
    return [_offre_to_response(o) for o in offres]


# ---------- Détail d'une offre ----------
@router.get("/{offre_id}", response_model=dict)
def get_offre(
    offre_id: str,
    db: Session = Depends(get_db),
):
    """Retourne une offre par ID. Public."""
    offre = db.query(OffreEmploi).filter(OffreEmploi.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")
    return _offre_to_response(offre)


# ---------- Création d'une offre (recruteur) ----------
@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_offre(
    body: OffreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("recruteur")),
):
    """Crée une offre (recruteur). Indexation Chroma automatique."""
    recruteur = get_recruteur_by_user_id(db, current_user.id)
    if not recruteur:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil recruteur introuvable")

    offre_id = str(uuid.uuid4())
    json_structure = _build_offre_json(body)

    offre = OffreEmploi(
        id=offre_id,
        recruteur_id=recruteur.id,
        titre=body.titre,
        description=body.description,
        localisation=body.localisation,
        type_contrat=body.type_contrat,
        salaire_min=body.salaire_min,
        salaire_max=body.salaire_max,
        experience_requise=body.experience_requise,
        statut="ouverte",
        json_structure=json_structure,
    )
    db.add(offre)
    db.commit()
    db.refresh(offre)

    try:
        index_offer(offre_id, json_structure, metadata={"recruteur_id": recruteur.id, "titre": body.titre})
    except Exception:
        pass

    return _offre_to_response(offre)


# ---------- Indexation Chroma ----------
@router.post("/index")
def index_offre(payload: OffreIndexRequest):
    """Indexe une offre dans Chroma."""
    index_offer(payload.offre_id, payload.offre, payload.metadata)
    return {"status": "ok", "indexed_id": payload.offre_id}


# ---------- Recherche de CVs pour une offre (sémantique) ----------
@router.post("/search-cvs")
def search_cvs(payload: OffreSearchCVRequest):
    """Retourne les CVs les plus pertinents pour une offre."""
    result = search_cvs_for_offer(payload.offre, top_k=payload.top_k)
    return result
