"""
Agent d'explication du matching avec LangChain
Génère des explications personnalisées pour recruteur et candidat
Membre 5 - Niveau 1 & 2
"""

import os
from typing import Dict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================
# SCHÉMAS PYDANTIC POUR EXPLICATIONS
# ============================================

class ExplicationRecruteur(BaseModel):
    """Explication destinée au recruteur"""
    recommandation: str = Field(description="RECRUTER, ENTRETIEN, ou REJETER")
    points_forts: list[str] = Field(description="3-5 points forts du candidat")
    points_faibles: list[str] = Field(description="2-4 points faibles ou manques")
    synthese: str = Field(description="Synthèse en 2-3 phrases")


class ExplicationCandidat(BaseModel):
    """Explication destinée au candidat"""
    message_principal: str = Field(description="Message encourageant ou constructif")
    competences_valorisees: list[str] = Field(description="Compétences qui correspondent")
    axes_amelioration: list[str] = Field(description="Compétences à développer")
    conseils: list[str] = Field(description="2-3 conseils concrets")


# ============================================
# PROMPTS LANGCHAIN
# ============================================

PROMPT_RECRUTEUR = """
Tu es un consultant RH expert. Tu dois analyser le matching entre un CV et une offre d'emploi, puis fournir une recommandation claire au recruteur.

SCORE DE MATCHING : {score_final}%
RECOMMANDATION SYSTÈME : {recommandation}

DÉTAILS DU MATCHING :
- Similarité sémantique : {similarite}%
- Compétences techniques : {comp_score}%
  - Compétences trouvées : {comp_trouvees}
  - Compétences manquantes : {comp_manquantes}
- Expérience : {exp_score}%
  - Candidat : {exp_candidat} ans
  - Requis : {exp_requis} ans
- Formation : {form_score}%
- Langues : {lang_score}%
  - Langues trouvées : {lang_trouvees}
  - Langues manquantes : {lang_manquantes}

NOM DU POSTE : {titre_poste}

Ta mission :
1. Identifier 3-5 POINTS FORTS du candidat (compétences, expérience, formation)
2. Identifier 2-4 POINTS FAIBLES ou manques critiques
3. Donner une RECOMMANDATION claire : "RECRUTER" (score > 80%), "ENTRETIEN" (50-80%), ou "REJETER" (< 50%)
4. Rédiger une SYNTHÈSE en 2-3 phrases maximum

Sois factuel, professionnel et direct. Base-toi uniquement sur les données fournies.

Retourne uniquement le JSON structuré.
"""


PROMPT_CANDIDAT = """
Tu es un coach de carrière bienveillant. Tu dois expliquer à un candidat pourquoi son profil correspond ou non à une offre d'emploi.

SCORE DE MATCHING : {score_final}%
RECOMMANDATION : {recommandation}

DÉTAILS DU MATCHING :
- Compétences trouvées : {comp_trouvees}
- Compétences manquantes : {comp_manquantes}
- Expérience : {exp_candidat} ans (requis : {exp_requis} ans)
- Langues trouvées : {lang_trouvees}
- Langues manquantes : {lang_manquantes}

POSTE VISÉ : {titre_poste}

Ta mission :
1. Rédiger un MESSAGE PRINCIPAL encourageant (si bon score) ou constructif (si faible score)
2. Lister les COMPÉTENCES VALORISÉES dans ce matching
3. Identifier les AXES D'AMÉLIORATION (compétences manquantes, expérience insuffisante, etc.)
4. Donner 2-3 CONSEILS CONCRETS pour améliorer le profil

RÈGLES :
- Reste positif et constructif, même si le score est faible
- Évite le jargon technique excessif
- Donne des conseils actionnables
- Encourage le candidat à progresser

Retourne uniquement le JSON structuré.
"""


# ============================================
# INITIALISATION DU LLM
# ============================================

def initialiser_llm():
    """Initialise le modèle LangChain avec Groq"""
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY absente du fichier .env")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,  # Un peu plus créatif pour les explications
        groq_api_key=GROQ_API_KEY,
        max_tokens=1500
    )
    return llm


# ============================================
# GÉNÉRATION DES EXPLICATIONS
# ============================================

def generer_explication_recruteur(
    score_final: float,
    details: Dict,
    recommandation: str,
    titre_poste: str
) -> Dict:
    """
    Génère une explication pour le recruteur.
    
    Args:
        score_final: Score de matching (0-100)
        details: Détails du scoring
        recommandation: EXCELLENT, BON, MOYEN, FAIBLE
        titre_poste: Titre du poste de l'offre
        
    Returns:
        Dict avec l'explication structurée
    """
    try:
        # Préparer les données pour le prompt
        comp_trouvees = ", ".join(details["competences"]["trouvees"]) or "Aucune"
        comp_manquantes = ", ".join(details["competences"]["manquantes"]) or "Aucune"
        lang_trouvees = ", ".join(details["langues"]["trouvees"]) or "Aucune"
        lang_manquantes = ", ".join(details["langues"]["manquantes"]) or "Aucune"
        
        # Créer la chaîne LangChain
        parser = JsonOutputParser(pydantic_object=ExplicationRecruteur)
        prompt = ChatPromptTemplate.from_template(PROMPT_RECRUTEUR)
        llm = initialiser_llm()
        chain = prompt | llm | parser
        
        # Invoquer le LLM
        resultat = chain.invoke({
            "score_final": score_final,
            "recommandation": recommandation,
            "similarite": details["similarite_semantique"],
            "comp_score": details["competences"]["score"],
            "comp_trouvees": comp_trouvees,
            "comp_manquantes": comp_manquantes,
            "exp_score": details["experience"]["score"],
            "exp_candidat": details["experience"]["annees_candidat"],
            "exp_requis": details["experience"]["annees_requises"],
            "form_score": details["formation"]["score"],
            "lang_score": details["langues"]["score"],
            "lang_trouvees": lang_trouvees,
            "lang_manquantes": lang_manquantes,
            "titre_poste": titre_poste
        })
        
        print("✅ Explication recruteur générée")
        return resultat
    
    except Exception as e:
        print(f"❌ Erreur génération explication recruteur: {e}")
        return explication_recruteur_fallback(score_final, recommandation)


def generer_explication_candidat(
    score_final: float,
    details: Dict,
    recommandation: str,
    titre_poste: str
) -> Dict:
    """
    Génère une explication pour le candidat.
    
    Args:
        score_final: Score de matching (0-100)
        details: Détails du scoring
        recommandation: EXCELLENT, BON, MOYEN, FAIBLE
        titre_poste: Titre du poste de l'offre
        
    Returns:
        Dict avec l'explication structurée
    """
    try:
        # Préparer les données pour le prompt
        comp_trouvees = ", ".join(details["competences"]["trouvees"]) or "Aucune compétence technique identifiée"
        comp_manquantes = ", ".join(details["competences"]["manquantes"]) or "Aucune"
        lang_trouvees = ", ".join(details["langues"]["trouvees"]) or "Non précisé"
        lang_manquantes = ", ".join(details["langues"]["manquantes"]) or "Aucune"
        
        # Créer la chaîne LangChain
        parser = JsonOutputParser(pydantic_object=ExplicationCandidat)
        prompt = ChatPromptTemplate.from_template(PROMPT_CANDIDAT)
        llm = initialiser_llm()
        chain = prompt | llm | parser
        
        # Invoquer le LLM
        resultat = chain.invoke({
            "score_final": score_final,
            "recommandation": recommandation,
            "comp_trouvees": comp_trouvees,
            "comp_manquantes": comp_manquantes,
            "exp_candidat": details["experience"]["annees_candidat"],
            "exp_requis": details["experience"]["annees_requises"],
            "lang_trouvees": lang_trouvees,
            "lang_manquantes": lang_manquantes,
            "titre_poste": titre_poste
        })
        
        print("✅ Explication candidat générée")
        return resultat
    
    except Exception as e:
        print(f"❌ Erreur génération explication candidat: {e}")
        return explication_candidat_fallback(score_final, details)


# ============================================
# FALLBACKS EN CAS D'ERREUR
# ============================================

def explication_recruteur_fallback(score: float, recommandation: str) -> Dict:
    """Explication de secours si le LLM échoue"""
    return {
        "recommandation": "ENTRETIEN" if score >= 50 else "REJETER",
        "points_forts": ["Profil analysé automatiquement"],
        "points_faibles": ["Analyse détaillée indisponible"],
        "synthese": f"Score de matching : {score}%. Recommandation : {recommandation}."
    }


def explication_candidat_fallback(score: float, details: Dict) -> Dict:
    """Explication de secours si le LLM échoue"""
    comp_manquantes = details["competences"]["manquantes"]
    
    return {
        "message_principal": f"Votre profil obtient un score de {score}% pour ce poste.",
        "competences_valorisees": details["competences"]["trouvees"][:3],
        "axes_amelioration": comp_manquantes[:3] if comp_manquantes else ["Continuez à développer vos compétences"],
        "conseils": [
            "Mettez à jour régulièrement votre CV",
            "Valorisez vos expériences pertinentes",
            "Développez les compétences demandées"
        ]
    }


# ============================================
# FONCTION PRINCIPALE
# ============================================

def generer_explications_completes(
    score_final: float,
    details: Dict,
    recommandation: str,
    titre_poste: str
) -> Dict:
    """
    Génère les explications complètes pour recruteur et candidat.
    
    Args:
        score_final: Score de matching (0-100)
        details: Détails du scoring
        recommandation: EXCELLENT, BON, MOYEN, FAIBLE
        titre_poste: Titre du poste
        
    Returns:
        Dict avec explications recruteur et candidat
    """
    print("\n🤖 Génération des explications IA...")
    
    explication_recruteur = generer_explication_recruteur(
        score_final,
        details,
        recommandation,
        titre_poste
    )
    
    explication_candidat = generer_explication_candidat(
        score_final,
        details,
        recommandation,
        titre_poste
    )
    
    return {
        "pour_recruteur": explication_recruteur,
        "pour_candidat": explication_candidat
    }