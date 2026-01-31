"""
API Dashboard : statistiques et données pour le tableau de bord recruteur.
VERSION DEBUG — logs détaillés pour identifier le problème.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.models.offre_emploi import OffreEmploi
from app.models.candidature import Candidature
from app.models.candidat import Candidat
from app.services.auth_service import get_recruteur_by_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _get_recruteur_or_raise(db: Session, current_user: User):
    """Récupère le recruteur ou lève une exception avec logs détaillés."""
    logger.info(f"[DASHBOARD] current_user.id = {current_user.id}")
    logger.info(f"[DASHBOARD] current_user.role = {current_user.role}")

    recruteur = get_recruteur_by_user_id(db, current_user.id)

    if not recruteur:
        logger.warning(f"[DASHBOARD] ❌ Aucun recruteur trouvé pour user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profil recruteur introuvable"
        )

    logger.info(f"[DASHBOARD] ✅ recruteur.id = {recruteur.id}")
    return recruteur


@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("recruteur")),
):
    """Statistiques principales du tableau de bord recruteur."""
    logger.info("[DASHBOARD] === GET /stats appelé ===")
    recruteur = _get_recruteur_or_raise(db, current_user)

    offres_ouvertes = db.query(func.count(OffreEmploi.id)).filter(
        OffreEmploi.recruteur_id == recruteur.id,
        OffreEmploi.statut == "ouverte"
    ).scalar() or 0
    logger.info(f"[DASHBOARD] offres_ouvertes = {offres_ouvertes}")

    total_candidatures = db.query(func.count(Candidature.id)).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id
    ).scalar() or 0
    logger.info(f"[DASHBOARD] total_candidatures = {total_candidatures}")

    candidatures_pending = db.query(func.count(Candidature.id)).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id,
        Candidature.statut == "pending"
    ).scalar() or 0

    candidatures_accepted = db.query(func.count(Candidature.id)).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id,
        Candidature.statut == "accepted"
    ).scalar() or 0

    seven_days_ago = datetime.now() - timedelta(days=7)
    candidatures_recentes = db.query(func.count(Candidature.id)).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id,
        Candidature.date_candidature >= seven_days_ago
    ).scalar() or 0

    result = {
        "offres_ouvertes": offres_ouvertes,
        "total_candidatures": total_candidatures,
        "candidatures_pending": candidatures_pending,
        "candidatures_accepted": candidatures_accepted,
        "candidatures_recentes": candidatures_recentes,
    }
    logger.info(f"[DASHBOARD] ✅ stats retournées : {result}")
    return result


@router.get("/top-candidats", response_model=list)
def get_top_candidats(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("recruteur")),
):
    """Top candidats par score de matching moyen."""
    logger.info("[DASHBOARD] === GET /top-candidats appelé ===")
    recruteur = _get_recruteur_or_raise(db, current_user)

    top_candidats = db.query(
        Candidat.id,
        Candidat.nom,
        Candidat.localisation,
        Candidat.telephone,
        func.avg(Candidature.score_matching).label("score_moyen"),
        func.count(Candidature.id).label("nombre_candidatures"),
        func.max(Candidature.score_matching).label("meilleur_score")
    ).join(
        Candidature, Candidat.id == Candidature.candidat_id
    ).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id,
        Candidature.score_matching.isnot(None)
    ).group_by(
        Candidat.id, Candidat.nom, Candidat.localisation, Candidat.telephone
    ).order_by(
        desc("score_moyen")
    ).limit(limit).all()

    logger.info(f"[DASHBOARD] ✅ top_candidats trouvés : {len(top_candidats)}")

    return [
        {
            "id": str(c.id),
            "nom": c.nom,
            "localisation": c.localisation,
            "telephone": c.telephone,
            "score_moyen": round(float(c.score_moyen), 2) if c.score_moyen else 0,
            "nombre_candidatures": c.nombre_candidatures,
            "meilleur_score": round(float(c.meilleur_score), 2) if c.meilleur_score else 0,
        }
        for c in top_candidats
    ]


@router.get("/dernieres-candidatures", response_model=list)
def get_dernieres_candidatures(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("recruteur")),
):
    """Dernières candidatures reçues."""
    logger.info("[DASHBOARD] === GET /dernieres-candidatures appelé ===")
    recruteur = _get_recruteur_or_raise(db, current_user)

    candidatures = db.query(
        Candidature.id,
        Candidature.statut,
        Candidature.score_matching,
        Candidature.date_candidature,
        Candidat.nom.label("candidat_nom"),
        Candidat.localisation.label("candidat_localisation"),
        OffreEmploi.titre.label("offre_titre"),
        OffreEmploi.id.label("offre_id")
    ).join(
        Candidat, Candidature.candidat_id == Candidat.id
    ).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id
    ).order_by(
        desc(Candidature.date_candidature)
    ).limit(limit).all()

    logger.info(f"[DASHBOARD] ✅ dernieres_candidatures trouvées : {len(candidatures)}")

    return [
        {
            "id": str(c.id),
            "candidat_nom": c.candidat_nom,
            "candidat_localisation": c.candidat_localisation,
            "offre_titre": c.offre_titre,
            "offre_id": str(c.offre_id),
            "statut": c.statut,
            "score_matching": round(float(c.score_matching), 2) if c.score_matching else None,
            "date_candidature": c.date_candidature.isoformat() if c.date_candidature else "",
        }
        for c in candidatures
    ]


@router.get("/liste-candidats", response_model=list)
def get_liste_candidats(
    offre_id: str | None = None,
    statut: str | None = None,
    min_score: float | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("recruteur")),
):
    """Liste complète des candidats avec filtres optionnels."""
    logger.info("[DASHBOARD] === GET /liste-candidats appelé ===")
    recruteur = _get_recruteur_or_raise(db, current_user)

    query = db.query(
        Candidat.id,
        Candidat.nom,
        Candidat.telephone,
        Candidat.localisation,
        Candidature.id.label("candidature_id"),
        Candidature.statut,
        Candidature.score_matching,
        Candidature.date_candidature,
        OffreEmploi.titre.label("offre_titre"),
        OffreEmploi.id.label("offre_id")
    ).join(
        Candidature, Candidat.id == Candidature.candidat_id
    ).join(
        OffreEmploi, Candidature.offre_id == OffreEmploi.id
    ).filter(
        OffreEmploi.recruteur_id == recruteur.id
    )

    if offre_id:
        query = query.filter(OffreEmploi.id == offre_id)
    if statut:
        query = query.filter(Candidature.statut == statut)
    if min_score is not None:
        query = query.filter(Candidature.score_matching >= min_score)

    candidats = query.order_by(desc(Candidature.date_candidature)).all()
    logger.info(f"[DASHBOARD] ✅ liste_candidats trouvés : {len(candidats)}")

    return [
        {
            "id": str(c.id),
            "nom": c.nom,
            "telephone": c.telephone,
            "localisation": c.localisation,
            "candidature_id": str(c.candidature_id),
            "statut": c.statut,
            "score_matching": round(float(c.score_matching), 2) if c.score_matching else None,
            "date_candidature": c.date_candidature.isoformat() if c.date_candidature else "",
            "offre_titre": c.offre_titre,
            "offre_id": str(c.offre_id),
        }
        for c in candidats
    ]