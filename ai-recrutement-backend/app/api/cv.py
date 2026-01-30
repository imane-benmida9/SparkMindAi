"""
API CV : upload PDF, liste mes CVs, détail, suppression, indexation Chroma.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.cv import CV
from app.services.auth_service import get_candidat_by_user_id
from app.ai.analyse_cv import analyser_cv_pdf, creer_cv_en_base
from app.vector_store.indexing import index_cv_from_json, search_offres_for_cv


router = APIRouter(prefix="/cvs", tags=["CVs"])


# ---------- Schémas ----------
class CVIndexRequest(BaseModel):
    cv_id: str = Field(..., description="ID du CV")
    cv_json: dict[str, Any] = Field(..., description="JSON structuré du CV")
    metadata: dict[str, Any] | None = None


class CVSearchOffresRequest(BaseModel):
    cv_json: dict[str, Any] = Field(..., description="JSON structuré du CV")
    top_k: int = Field(default=10, ge=1, le=50)


class CVResponse(BaseModel):
    id: str
    candidat_id: str
    nom_fichier: str
    texte_brut: str | None
    extracted_data: dict | None  # alias pour le front
    json_structure: dict | None
    date_upload: str

    class Config:
        from_attributes = True


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


# ---------- Upload PDF (analyse + sauvegarde BDD + index Chroma) ----------
@router.post("/upload", response_model=dict)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Upload un CV PDF : extraction IA, sauvegarde en BDD, indexation Chroma."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier PDF requis")

    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil candidat introuvable")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 Mo
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier trop volumineux (max 10 Mo)")

    try:
        cv_json, texte_brut, _ = analyser_cv_pdf(content, file.filename or "cv.pdf", sauvegarder_pdf=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Erreur lors de l'analyse du CV : {str(e)}",
        )

    json_dict = cv_json if isinstance(cv_json, dict) else (cv_json.model_dump() if hasattr(cv_json, "model_dump") else {})
    try:
        nouveau_cv = creer_cv_en_base(
            db, candidat.id, file.filename or "cv.pdf", texte_brut, json_dict, fichier_chemin=None
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    try:
        index_cv_from_json(
            str(nouveau_cv.id),
            json_dict,
            metadata={"candidat_id": candidat.id, "nom_fichier": file.filename},
        )
    except Exception:
        pass  # indexation non bloquante

    return {
        "id": nouveau_cv.id,
        "candidat_id": nouveau_cv.candidat_id,
        "nom_fichier": nouveau_cv.fichier_nom,
        "extracted_data": nouveau_cv.json_structure,
        "json_structure": nouveau_cv.json_structure,
    }


# ---------- Liste des CVs du candidat connecté ----------
@router.get("/my-cvs", response_model=list)
def my_cvs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Retourne la liste des CVs du candidat connecté."""
    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profil candidat introuvable")

    cvs = db.query(CV).filter(CV.candidat_id == candidat.id).order_by(CV.date_upload.desc()).all()
    return [_cv_to_response(c) for c in cvs]


# ---------- Détail d'un CV ----------
@router.get("/{cv_id}", response_model=dict)
def get_cv(
    cv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retourne un CV par ID (candidat : uniquement les siens)."""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV introuvable")

    candidat = get_candidat_by_user_id(db, current_user.id)
    if current_user.role.value == "candidat" and (not candidat or cv.candidat_id != candidat.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")

    return _cv_to_response(cv)


# ---------- Suppression ----------
@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cv(
    cv_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("candidat")),
):
    """Supprime un CV (candidat : uniquement les siens)."""
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV introuvable")

    candidat = get_candidat_by_user_id(db, current_user.id)
    if not candidat or cv.candidat_id != candidat.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")

    db.delete(cv)
    db.commit()
    return None


# ---------- Indexation Chroma (pour sync manuel si besoin) ----------
@router.post("/index")
def index_cv(payload: CVIndexRequest):
    """Indexe un CV (JSON) dans Chroma pour la recherche sémantique."""
    index_cv_from_json(payload.cv_id, payload.cv_json, payload.metadata)
    return {"status": "ok", "indexed_id": payload.cv_id}


# ---------- Recherche d'offres pour un CV (sémantique) ----------
@router.post("/search-offres")
def search_offres(payload: CVSearchOffresRequest):
    """Retourne les offres les plus pertinentes pour un CV (JSON)."""
    result = search_offres_for_cv(payload.cv_json, top_k=payload.top_k)
    return result
