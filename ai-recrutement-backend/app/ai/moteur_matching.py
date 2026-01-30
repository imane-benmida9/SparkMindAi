
"""
Moteur de matching CV-Offre
Membre 5 - Niveau 2
Orchestre : scoring + embeddings + explications IA
"""

from typing import Dict, List, Optional
import numpy as np

from app.utils.scoring import (
    calculer_score_final,
    determiner_recommandation
)
from app.ai.agent_explication import generer_explications_completes
from app.ai.embeddings import embed_text


# ============================================
# CALCUL DE SIMILARITÉ SÉMANTIQUE
# ============================================

def calculer_similarite_cosinus(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calcule la similarité cosinus entre deux embeddings.
    
    Args:
        embedding1: Premier vecteur
        embedding2: Deuxième vecteur
        
    Returns:
        float: Similarité entre 0 et 1
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Similarité cosinus
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarite = dot_product / (norm1 * norm2)
    
    # Normaliser entre 0 et 1
    similarite_normalisee = (similarite + 1) / 2
    
    return float(similarite_normalisee)


# ============================================
# PRÉPARATION DES TEXTES POUR EMBEDDINGS
# ============================================

def preparer_texte_cv(cv_json: Dict) -> str:
    """
    Crée une représentation textuelle du CV pour embedding.
    
    Args:
        cv_json: Structure JSON du CV
        
    Returns:
        str: Texte représentatif du CV
    """
    parties = []
    
    # Compétences
    competences = cv_json.get("competences", [])
    if competences:
        parties.append("Compétences : " + ", ".join(competences))
    
    # Expériences
    experiences = cv_json.get("experiences", [])
    for exp in experiences:
        poste = exp.get("poste", "")
        description = exp.get("description", "")
        if poste:
            parties.append(f"Expérience : {poste}")
        if description:
            parties.append(description)
    
    # Formations
    formations = cv_json.get("formations", [])
    for form in formations:
        diplome = form.get("diplome", "")
        if diplome:
            parties.append(f"Formation : {diplome}")
    
    # Langues
    langues = cv_json.get("langues", [])
    if langues:
        parties.append("Langues : " + ", ".join(langues))
    
    return " | ".join(parties)


def preparer_texte_offre(offre_json: Dict) -> str:
    """
    Crée une représentation textuelle de l'offre pour embedding.
    
    Args:
        offre_json: Structure JSON de l'offre
        
    Returns:
        str: Texte représentatif de l'offre
    """
    parties = []
    
    # Titre
    titre = offre_json.get("titre", "")
    if titre:
        parties.append(f"Poste : {titre}")
    
    # Description
    description = offre_json.get("description", "")
    if description:
        parties.append(description)
    
    # Compétences requises
    competences = offre_json.get("competences_requises", [])
    if competences:
        parties.append("Compétences requises : " + ", ".join(competences))
    
    # Missions
    missions = offre_json.get("missions", "")
    if missions:
        parties.append(f"Missions : {missions}")
    
    # Langues
    langues = offre_json.get("langues_requises", [])
    if langues:
        parties.append("Langues : " + ", ".join(langues))
    
    return " | ".join(parties)


# ============================================
# FONCTION PRINCIPALE DE MATCHING
# ============================================

def executer_matching(
    cv_json: Dict,
    offre_json: Dict,
    cv_embedding: Optional[List[float]] = None,
    offre_embedding: Optional[List[float]] = None,
    generer_explications: bool = True
) -> Dict:
    """
    Exécute le matching complet entre un CV et une offre.
    
    Args:
        cv_json: Structure JSON du CV
        offre_json: Structure JSON de l'offre
        cv_embedding: Embedding du CV (optionnel, sera calculé si absent)
        offre_embedding: Embedding de l'offre (optionnel, sera calculé si absent)
        generer_explications: Si True, génère les explications IA
        
    Returns:
        Dict avec score, détails et explications
    """
    print("\n" + "=" * 70)
    print("🎯 DÉMARRAGE DU MATCHING")
    print("=" * 70)
    
    # Étape 1 : Calculer les embeddings si nécessaire
    if cv_embedding is None:
        print("📊 Génération embedding CV...")
        texte_cv = preparer_texte_cv(cv_json)
        cv_embedding = embed_text(texte_cv)
    
    if offre_embedding is None:
        print("📊 Génération embedding offre...")
        texte_offre = preparer_texte_offre(offre_json)
        offre_embedding = embed_text(texte_offre)
    
    # Étape 2 : Calculer la similarité sémantique
    print("🔍 Calcul de similarité sémantique...")
    similarite_semantique = calculer_similarite_cosinus(cv_embedding, offre_embedding)
    print(f"   → Similarité : {similarite_semantique * 100:.2f}%")
    
    # Étape 3 : Calculer le score final
    print("📈 Calcul du score final...")
    resultat_scoring = calculer_score_final(
        similarite_semantique,
        cv_json,
        offre_json
    )
    
    score_final = resultat_scoring["score_final"]
    details = resultat_scoring["details"]
    
    print(f"   → Score final : {score_final}%")
    
    # Étape 4 : Déterminer la recommandation
    recommandation = determiner_recommandation(score_final)
    print(f"   → Recommandation : {recommandation}")
    
    # Étape 5 : Générer les explications IA
    explications = None
    if generer_explications:
        titre_poste = offre_json.get("titre", "Poste sans titre")
        explications = generer_explications_completes(
            score_final,
            details,
            recommandation,
            titre_poste
        )
    
    # Construire la réponse finale
    resultat_final = {
        "score_final": score_final,
        "recommandation": recommandation,
        "details": details,
        "explications": explications
    }
    
    print("=" * 70)
    print("✅ MATCHING TERMINÉ")
    print("=" * 70)
    
    return resultat_final


def executer_matching_avec_recherche(cv_json: Dict, top_k: int = 10) -> Dict:
    """
    Recherche d'offres compatibles pour un CV donné
    """
    # Pour le moment, retourne une version simplifiée
    print(f"🔍 Recherche d'offres pour CV (top_k={top_k})")
    
    # Utilise la fonction de recherche vectorielle si disponible
    try:
        from app.vector_store.indexing import search_offres_for_cv
        result = search_offres_for_cv(cv_json, top_k)
        return result
    except ImportError:
        # Fallback si la recherche vectorielle n'est pas disponible
        return {
            "offres": [],
            "total_results": 0,
            "message": "Recherche vectorielle non disponible en mode développement"
        }