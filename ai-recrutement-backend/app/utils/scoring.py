
"""
Module de calcul de score de matching CV-Offre
Membre 5 - Niveau 1 & 2
"""

from typing import Dict, List, Tuple
import re


# ============================================
# PONDÉRATIONS DU SCORING
# ============================================

PONDERATIONS = {
    "similarite_semantique": 0.40,  # 40% - Similarité vectorielle
    "competences_techniques": 0.25,  # 25% - Match des compétences
    "experience": 0.20,              # 20% - Années d'expérience
    "formation": 0.10,               # 10% - Niveau d'études
    "langues": 0.05                  # 5% - Langues requises
}


# ============================================
# EXTRACTION DES ANNÉES D'EXPÉRIENCE
# ============================================

def extraire_annees_experience(experiences: List[Dict]) -> int:
    """
    Calcule le nombre d'années d'expérience totales.
    
    Args:
        experiences: Liste des expériences du CV
        
    Returns:
        int: Nombre d'années d'expérience (estimation)
    """
    if not experiences:
        return 0
    
    total_annees = 0
    
    for exp in experiences:
        periode = exp.get("periode", "")
        if not periode:
            continue
        
        # Chercher des patterns comme "2020-2023", "3 ans", etc.
        # Pattern: année début - année fin
        match_annees = re.findall(r'\b(20\d{2})\b', periode)
        if len(match_annees) >= 2:
            try:
                debut = int(match_annees[0])
                fin = int(match_annees[-1])
                total_annees += max(0, fin - debut)
            except:
                pass
        
        # Pattern: "X ans" ou "X années"
        match_duree = re.search(r'(\d+)\s*an', periode.lower())
        if match_duree:
            total_annees += int(match_duree.group(1))
    
    # Si aucune extraction, estimer à 2 ans par expérience
    if total_annees == 0 and experiences:
        total_annees = len(experiences) * 2
    
    return total_annees


# ============================================
# MATCHING DES COMPÉTENCES
# ============================================

def normaliser_competence(comp: str) -> str:
    """Normalise une compétence pour la comparaison"""
    return comp.lower().strip().replace("-", "").replace("_", "")


def calculer_match_competences(
    competences_cv: List[str],
    competences_requises: List[str]
) -> Tuple[float, List[str], List[str]]:
    """
    Calcule le taux de match des compétences.
    
    Args:
        competences_cv: Compétences du candidat
        competences_requises: Compétences demandées dans l'offre
        
    Returns:
        Tuple: (score, competences_trouvees, competences_manquantes)
    """
    if not competences_requises:
        return 1.0, [], []
    
    if not competences_cv:
        return 0.0, [], competences_requises
    
    # Normaliser les compétences
    cv_norm = {normaliser_competence(c): c for c in competences_cv}
    req_norm = {normaliser_competence(c): c for c in competences_requises}
    
    # Trouver les matches
    competences_trouvees = []
    competences_manquantes = []
    
    for comp_norm, comp_orig in req_norm.items():
        if comp_norm in cv_norm:
            competences_trouvees.append(comp_orig)
        else:
            # Vérifier si une compétence similaire existe (contient ou est contenue)
            trouve = False
            for cv_comp_norm in cv_norm.keys():
                if comp_norm in cv_comp_norm or cv_comp_norm in comp_norm:
                    competences_trouvees.append(comp_orig)
                    trouve = True
                    break
            
            if not trouve:
                competences_manquantes.append(comp_orig)
    
    # Calculer le score
    score = len(competences_trouvees) / len(competences_requises)
    
    return score, competences_trouvees, competences_manquantes


# ============================================
# MATCHING DE FORMATION
# ============================================

def extraire_niveau_formation(formations: List[Dict]) -> int:
    """
    Extrait le niveau de formation le plus élevé.
    
    Returns:
        int: 0-5 (0=aucun, 1=bac, 2=bac+2, 3=licence, 4=master, 5=doctorat)
    """
    if not formations:
        return 0
    
    niveau_max = 0
    
    for formation in formations:
        diplome = formation.get("diplome", "").lower()
        
        if any(mot in diplome for mot in ["doctorat", "phd", "thèse"]):
            niveau_max = max(niveau_max, 5)
        elif any(mot in diplome for mot in ["master", "m2", "m1", "ingénieur"]):
            niveau_max = max(niveau_max, 4)
        elif any(mot in diplome for mot in ["licence", "bachelor", "l3"]):
            niveau_max = max(niveau_max, 3)
        elif any(mot in diplome for mot in ["dut", "bts", "deug", "bac+2"]):
            niveau_max = max(niveau_max, 2)
        elif any(mot in diplome for mot in ["bac", "baccalauréat"]):
            niveau_max = max(niveau_max, 1)
    
    return niveau_max


def calculer_score_formation(niveau_cv: int, niveau_requis: int) -> float:
    """
    Compare le niveau de formation.
    
    Returns:
        float: Score entre 0 et 1
    """
    if niveau_requis == 0:
        return 1.0
    
    if niveau_cv >= niveau_requis:
        return 1.0
    elif niveau_cv == niveau_requis - 1:
        return 0.7
    elif niveau_cv == niveau_requis - 2:
        return 0.4
    else:
        return 0.2


# ============================================
# MATCHING DES LANGUES
# ============================================

def calculer_match_langues(
    langues_cv: List[str],
    langues_requises: List[str]
) -> Tuple[float, List[str], List[str]]:
    """
    Calcule le match des langues.
    
    Returns:
        Tuple: (score, langues_trouvees, langues_manquantes)
    """
    if not langues_requises:
        return 1.0, [], []
    
    if not langues_cv:
        return 0.0, [], langues_requises
    
    # Normaliser
    cv_norm = {normaliser_competence(l.split()[0]): l for l in langues_cv}
    req_norm = {normaliser_competence(l.split()[0]): l for l in langues_requises}
    
    langues_trouvees = []
    langues_manquantes = []
    
    for lang_norm, lang_orig in req_norm.items():
        if lang_norm in cv_norm:
            langues_trouvees.append(lang_orig)
        else:
            langues_manquantes.append(lang_orig)
    
    score = len(langues_trouvees) / len(langues_requises) if langues_requises else 1.0
    
    return score, langues_trouvees, langues_manquantes


# ============================================
# CALCUL DU SCORE FINAL
# ============================================

def calculer_score_final(
    similarite_semantique: float,
    cv_json: Dict,
    offre_json: Dict
) -> Dict:
    """
    Calcule le score final de matching en combinant tous les critères.
    
    Args:
        similarite_semantique: Score de similarité vectorielle (0-1)
        cv_json: Structure JSON du CV
        offre_json: Structure JSON de l'offre
        
    Returns:
        Dict avec score final et détails
    """
    
    # 1. Similarité sémantique (déjà calculée par Chroma)
    score_semantique = similarite_semantique
    
    # 2. Compétences techniques
    competences_cv = cv_json.get("competences", [])
    competences_requises = offre_json.get("competences_requises", [])
    
    score_comp, comp_trouvees, comp_manquantes = calculer_match_competences(
        competences_cv,
        competences_requises
    )
    
    # 3. Expérience
    annees_cv = extraire_annees_experience(cv_json.get("experiences", []))
    annees_requises = offre_json.get("experience_requise_ans", 0)
    
    if annees_requises == 0:
        score_exp = 1.0
    elif annees_cv >= annees_requises:
        score_exp = 1.0
    elif annees_cv >= annees_requises * 0.7:
        score_exp = 0.8
    elif annees_cv >= annees_requises * 0.5:
        score_exp = 0.5
    else:
        score_exp = max(0.2, annees_cv / annees_requises)
    
    # 4. Formation
    niveau_cv = extraire_niveau_formation(cv_json.get("formations", []))
    niveau_requis = offre_json.get("niveau_etudes_requis", 0)
    score_formation = calculer_score_formation(niveau_cv, niveau_requis)
    
    # 5. Langues
    langues_cv = cv_json.get("langues", [])
    langues_requises = offre_json.get("langues_requises", [])
    score_langues, langues_ok, langues_manq = calculer_match_langues(
        langues_cv,
        langues_requises
    )
    
    # Calcul du score final pondéré
    score_final = (
        PONDERATIONS["similarite_semantique"] * score_semantique +
        PONDERATIONS["competences_techniques"] * score_comp +
        PONDERATIONS["experience"] * score_exp +
        PONDERATIONS["formation"] * score_formation +
        PONDERATIONS["langues"] * score_langues
    )
    
    # Arrondir à 2 décimales et convertir en pourcentage
    score_final = round(score_final * 100, 2)
    
    return {
        "score_final": score_final,
        "details": {
            "similarite_semantique": round(score_semantique * 100, 2),
            "competences": {
                "score": round(score_comp * 100, 2),
                "trouvees": comp_trouvees,
                "manquantes": comp_manquantes
            },
            "experience": {
                "score": round(score_exp * 100, 2),
                "annees_candidat": annees_cv,
                "annees_requises": annees_requises
            },
            "formation": {
                "score": round(score_formation * 100, 2),
                "niveau_candidat": niveau_cv,
                "niveau_requis": niveau_requis
            },
            "langues": {
                "score": round(score_langues * 100, 2),
                "trouvees": langues_ok,
                "manquantes": langues_manq
            }
        }
    }


# ============================================
# DÉTERMINATION DE LA RECOMMANDATION
# ============================================

def determiner_recommandation(score_final: float) -> str:
    """
    Détermine la recommandation basée sur le score.
    
    Returns:
        str: "EXCELLENT", "BON", "MOYEN", "FAIBLE"
    """
    if score_final >= 80:
        return "EXCELLENT"
    elif score_final >= 65:
        return "BON"
    elif score_final >= 50:
        return "MOYEN"
    else:
        return "FAIBLE"
