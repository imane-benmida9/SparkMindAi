
"""
Schémas Pydantic pour les réponses de matching
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================
# DÉTAILS DU SCORING
# ============================================

class CompetencesDetail(BaseModel):
    """Détails du matching des compétences"""
    score: float = Field(description="Score de matching des compétences (0-100)")
    trouvees: List[str] = Field(default=[], description="Compétences du CV qui matchent")
    manquantes: List[str] = Field(default=[], description="Compétences requises manquantes")


class ExperienceDetail(BaseModel):
    """Détails du matching de l'expérience"""
    score: float = Field(description="Score d'expérience (0-100)")
    annees_candidat: int = Field(description="Années d'expérience du candidat")
    annees_requises: int = Field(description="Années d'expérience requises")


class FormationDetail(BaseModel):
    """Détails du matching de la formation"""
    score: float = Field(description="Score de formation (0-100)")
    niveau_candidat: int = Field(description="Niveau de formation du candidat (0-5)")
    niveau_requis: int = Field(description="Niveau de formation requis (0-5)")


class LanguesDetail(BaseModel):
    """Détails du matching des langues"""
    score: float = Field(description="Score de langues (0-100)")
    trouvees: List[str] = Field(default=[], description="Langues maîtrisées qui matchent")
    manquantes: List[str] = Field(default=[], description="Langues requises manquantes")


class DetailsScoring(BaseModel):
    """Détails complets du scoring"""
    similarite_semantique: float = Field(description="Similarité sémantique (0-100)")
    competences: CompetencesDetail
    experience: ExperienceDetail
    formation: FormationDetail
    langues: LanguesDetail


# ============================================
# EXPLICATIONS IA
# ============================================

class ExplicationRecruteur(BaseModel):
    """Explication destinée au recruteur"""
    recommandation: str = Field(description="RECRUTER, ENTRETIEN, ou REJETER")
    points_forts: List[str] = Field(description="Points forts du candidat")
    points_faibles: List[str] = Field(description="Points faibles ou manques")
    synthese: str = Field(description="Synthèse globale")


class ExplicationCandidat(BaseModel):
    """Explication destinée au candidat"""
    message_principal: str = Field(description="Message principal")
    competences_valorisees: List[str] = Field(description="Compétences qui correspondent")
    axes_amelioration: List[str] = Field(description="Axes d'amélioration")
    conseils: List[str] = Field(description="Conseils concrets")


class Explications(BaseModel):
    """Explications complètes"""
    pour_recruteur: ExplicationRecruteur
    pour_candidat: ExplicationCandidat


# ============================================
# RÉPONSE COMPLÈTE DE MATCHING
# ============================================

class MatchingResponse(BaseModel):
    """Réponse complète d'un matching CV-Offre"""
    score_final: float = Field(description="Score final de matching (0-100)")
    recommandation: str = Field(description="EXCELLENT, BON, MOYEN, ou FAIBLE")
    details: DetailsScoring
    explications: Optional[Explications] = Field(
        default=None,
        description="Explications générées par IA"
    )


class MatchingListResponse(BaseModel):
    """Réponse pour une liste de matchings"""
    cv_id: Optional[str] = None
    offre_id: Optional[str] = None
    matches: List[MatchingResponse]
    total_results: int


# ============================================
# REQUÊTES
# ============================================

class MatchingRequest(BaseModel):
    """Requête pour exécuter un matching"""
    cv_id: str = Field(description="ID du CV")
    offre_id: str = Field(description="ID de l'offre")
    generer_explications: bool = Field(
        default=True,
        description="Générer les explications IA"
    )


class SearchMatchingRequest(BaseModel):
    """Requête pour rechercher les meilleurs matches"""
    cv_id: str = Field(description="ID du CV à matcher")
    top_k: int = Field(default=5, ge=1, le=20, description="Nombre de résultats")
    generer_explications: bool = Field(
        default=True,
        description="Générer les explications IA"
    )
