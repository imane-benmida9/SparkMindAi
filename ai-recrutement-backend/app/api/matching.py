
"""
API Endpoints pour le matching CV-Offre
Membre 5 - Niveau 2
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.matching import (
    MatchingRequest,
    MatchingResponse,
    SearchMatchingRequest,
    MatchingListResponse,
)
from pydantic import BaseModel, Field
from app.ai.moteur_matching import executer_matching, executer_matching_avec_recherche
from app.ai.embeddings import embed_text


router = APIRouter(prefix="/matching", tags=["Matching"])


# ============================================
# MATCHING SIMPLE : 1 CV vs 1 OFFRE
# ============================================

@router.post("/score", response_model=MatchingResponse)
async def calculer_matching(
    request: MatchingRequest,
    db: Session = Depends(get_db)
):
    """
    Calcule le score de matching entre un CV et une offre.
    
    Retourne :
    - Score final (0-100)
    - Détails par critère
    - Explications IA pour recruteur et candidat
    """
    try:
        # Récupérer le CV depuis la base
        from app.models.cv import CV
        cv = db.query(CV).filter(CV.id == request.cv_id).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CV {request.cv_id} introuvable"
            )
        
        # Récupérer l'offre depuis la base
        from app.models.offre_emploi import OffreEmploi
        offre = db.query(OffreEmploi).filter(OffreEmploi.id == request.offre_id).first()
        
        if not offre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Offre {request.offre_id} introuvable"
            )
        
        # Exécuter le matching (embeddings calculés à la volée si non stockés en BDD)
        cv_embedding = getattr(cv, "embedding", None)
        offre_embedding = getattr(offre, "embedding", None)
        resultat = executer_matching(
            cv_json=cv.json_structure or {},
            offre_json=offre.json_structure or {"titre": offre.titre, "description": offre.description},
            cv_embedding=cv_embedding,
            offre_embedding=offre_embedding,
            generer_explications=request.generer_explications
        )
        
        return MatchingResponse(**resultat)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching : {str(e)}"
        )


# ============================================
# MATCHING AVANCÉ : 1 CV vs TOUTES LES OFFRES
# ============================================

@router.post("/search-offres", response_model=MatchingListResponse)
async def rechercher_meilleures_offres(
    request: SearchMatchingRequest,
    db: Session = Depends(get_db)
):
    """
    Trouve les meilleures offres pour un CV donné.
    
    Utilise ChromaDB pour une recherche vectorielle rapide.
    """
    try:
        # Récupérer le CV
        from app.models.cv import CV
        cv = db.query(CV).filter(CV.id == request.cv_id).first()
        
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CV {request.cv_id} introuvable"
            )
        
        # Récupérer toutes les offres actives
        from app.models.offre_emploi import OffreEmploi
        offres = db.query(OffreEmploi).filter(OffreEmploi.statut == "ouverte").all()
        
        if not offres:
            return MatchingListResponse(
                cv_id=request.cv_id,
                matches=[],
                total_results=0
            )
        
        # Exécuter le matching pour chaque offre, puis trier et garder top_k
        matches = []
        for offre in offres:
            resultat = executer_matching(
                cv_json=cv.json_structure or {},
                offre_json=offre.json_structure or {"titre": offre.titre, "description": offre.description},
                cv_embedding=getattr(cv, "embedding", None),
                offre_embedding=getattr(offre, "embedding", None),
                generer_explications=request.generer_explications
            )
            matches.append(MatchingResponse(**resultat))
        
        matches.sort(key=lambda x: x.score_final, reverse=True)
        top_matches = matches[: request.top_k]
        
        return MatchingListResponse(
            cv_id=request.cv_id,
            matches=top_matches,
            total_results=len(matches)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche : {str(e)}"
        )


# ============================================
# MATCHING INVERSE : 1 OFFRE vs TOUS LES CV
# ============================================

@router.post("/search-candidats/{offre_id}", response_model=MatchingListResponse)
async def rechercher_meilleurs_candidats(
    offre_id: str,
    top_k: int = 10,
    generer_explications: bool = True,
    db: Session = Depends(get_db)
):
    """
    Trouve les meilleurs candidats pour une offre donnée.
    
    Utile pour les recruteurs qui veulent voir les CV les plus pertinents.
    """
    try:
        # Récupérer l'offre
        from app.models.offre_emploi import OffreEmploi
        offre = db.query(OffreEmploi).filter(OffreEmploi.id == offre_id).first()
        
        if not offre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Offre {offre_id} introuvable"
            )
        
        # Récupérer tous les CV
        from app.models.cv import CV
        cvs = db.query(CV).all()
        
        if not cvs:
            return MatchingListResponse(
                offre_id=offre_id,
                matches=[],
                total_results=0
            )
        
        # Exécuter le matching pour chaque CV
        matches = []
        
        for cv in cvs:
            resultat = executer_matching(
                cv_json=cv.json_structure or {},
                offre_json=offre.json_structure or {"titre": offre.titre, "description": offre.description},
                cv_embedding=getattr(cv, "embedding", None),
                offre_embedding=getattr(offre, "embedding", None),
                generer_explications=generer_explications
            )
            
            matches.append(MatchingResponse(**resultat))
        
        # Trier par score décroissant
        matches.sort(key=lambda x: x.score_final, reverse=True)
        
        return MatchingListResponse(
            offre_id=offre_id,
            matches=matches[:top_k],
            total_results=len(matches)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche : {str(e)}"
        )


# ============================================
# COMPAT FRONTEND : candidate + job (sans cv_id/offre_id)
# ============================================

class MatchCompatRequest(BaseModel):
    candidate: dict = Field(default_factory=dict)
    job: dict = Field(default_factory=dict)


@router.post("/match", response_model=MatchingResponse)
async def match_candidate_to_offer(request: MatchCompatRequest):
    """
    Matching à partir d'objets candidate/job (compat frontend).
    Utilise les champs skills, experience, education pour construire cv_json et offre_json.
    """
    c = request.candidate
    j = request.job
    skills_c = c.get("skills") or []
    skills_j = j.get("skills") or []
    cv_json = {
        "competences": skills_c if isinstance(skills_c, list) else (skills_c.split(",") if isinstance(skills_c, str) else []),
        "experiences": [{"periode": f"{c.get('experience', 0)} ans", "description": ""}],
        "formations": [{"diplome": c.get("education", "")}],
        "langues": [],
    }
    offre_json = {
        "titre": "Poste",
        "description": "",
        "competences_requises": skills_j if isinstance(skills_j, list) else (skills_j.split(",") if isinstance(skills_j, str) else []),
        "experience_requise": j.get("experience", 0),
        "niveau_etude": j.get("education", ""),
    }
    try:
        resultat = executer_matching(cv_json, offre_json, cv_embedding=None, offre_embedding=None, generer_explications=True)
        return MatchingResponse(**resultat)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur matching : {str(e)}"
        )


# ============================================
# ENDPOINT DE TEST
# ============================================

@router.post("/test")
async def tester_matching(
    cv_json: dict,
    offre_json: dict,
    generer_explications: bool = True
):
    """
    Endpoint de test pour le matching sans accès à la base de données.
    
    Permet de tester le moteur de matching avec des données JSON directes.
    """
    try:
        resultat = executer_matching(
            cv_json=cv_json,
            offre_json=offre_json,
            generer_explications=generer_explications
        )
        
        return MatchingResponse(**resultat)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du test : {str(e)}"
        )
