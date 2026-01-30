"""
Agent d'analyse d'offres d'emploi par IA générative avec LangChain.
Membre 3 - Niveau 1 & 2
- Analyse et structuration des offres d'emploi
- Stockage du JSON en base de données
"""

import os
import json
from typing import Dict, Optional, List, Union
from dotenv import load_dotenv

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


# Charger les variables d'environnement
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================
# SCHÉMA PYDANTIC POUR VALIDATION
# ============================================

class OffreEmploiStructure(BaseModel):
    """Schéma complet d'une offre d'emploi"""
    titre: str = Field(description="Titre du poste")
    description: str = Field(description="Description détaillée du poste")
    competences_requises: List[str] = Field(default=[], description="Compétences techniques requises")
    experience_requise_ans: int = Field(default=0, description="Années d'expérience requises")
    niveau_etudes_requis: int = Field(default=0, description="Niveau d'études requis (0-5)")
    langues_requises: List[Union[str, Dict[str, str]]] = Field(default=[], description="Langues requises")
    missions: Optional[Union[str, List[str]]] = Field(default=None, description="Missions principales du poste")
    localisation: Optional[str] = Field(default=None, description="Lieu de travail")
    type_contrat: Optional[str] = Field(default=None, description="Type de contrat (CDI, CDD, etc.)")
    salaire_min: Optional[float] = Field(default=None, description="Salaire minimum")
    salaire_max: Optional[float] = Field(default=None, description="Salaire maximum")


# ============================================
# PROMPT LANGCHAIN
# ============================================

PROMPT_TEMPLATE = """
Tu es un expert en analyse d'offres d'emploi. Ta mission est d'extraire TOUTES les informations d'une offre d'emploi et de les structurer en JSON.

RÈGLES IMPORTANTES :
1. Extrais TOUTES les compétences techniques mentionnées (langages, frameworks, outils)
2. Identifie clairement le nombre d'années d'expérience requis (si mentionné, sinon 0)
3. Détermine le niveau d'études requis selon cette échelle :
   - 0 : Aucun diplôme spécifique
   - 1 : Baccalauréat
   - 2 : Bac+2 (BTS, DUT)
   - 3 : Licence (Bac+3)
   - 4 : Master / Ingénieur (Bac+5)
   - 5 : Doctorat (Bac+8)
4. Liste toutes les langues requises avec leur niveau si mentionné
5. Si une information n'est pas présente, utilise null ou une liste vide [] ou 0 pour les nombres
6. Sois exhaustif et précis

STRUCTURE ATTENDUE :
- titre: Titre du poste
- description: Description complète du poste
- competences_requises: Liste des compétences techniques
- experience_requise_ans: Nombre d'années d'expérience (nombre entier, 0 si non spécifié)
- niveau_etudes_requis: Niveau d'études (0-5 selon l'échelle ci-dessus)
- langues_requises: Liste des langues avec niveau si disponible
- missions: Missions principales du poste
- localisation: Lieu de travail
- type_contrat: Type de contrat (CDI, CDD, Stage, etc.)
- salaire_min: Salaire minimum (nombre ou null)
- salaire_max: Salaire maximum (nombre ou null)

OFFRE D'EMPLOI À ANALYSER :
{offre_text}

Retourne uniquement le JSON structuré selon le schéma défini.
"""


# ============================================
# CONFIGURATION LANGCHAIN
# ============================================

def initialiser_llm():
    """Initialise le modèle LangChain avec Groq"""
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY absente du fichier .env")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        groq_api_key=GROQ_API_KEY,
        max_tokens=2000
    )
    return llm


def creer_chaine_extraction_offre():
    """Crée la chaîne LangChain pour l'extraction d'offre"""
    parser = JsonOutputParser(pydantic_object=OffreEmploiStructure)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = initialiser_llm()
    chain = prompt | llm | parser
    return chain


# ============================================
# FONCTIONS D'EXTRACTION
# ============================================

def analyser_offre_texte(texte_offre: str) -> Dict:
    """
    Analyse une offre d'emploi texte avec LangChain et retourne un JSON structuré.
    
    Args:
        texte_offre: Contenu texte de l'offre
        
    Returns:
        dict: Offre structurée selon OffreEmploiStructure
    """
    try:
        print("🔄 Création de la chaîne LangChain pour offre...")
        chain = creer_chaine_extraction_offre()
        
        print("🤖 Envoi à Groq via LangChain...")
        resultat = chain.invoke({"offre_text": texte_offre})
        
        print("✅ Réponse reçue et parsée")
        return resultat
    
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse LangChain: {str(e)}")
        return structure_offre_vide()


def analyser_offre_complete(
    titre: str,
    description: str,
    **kwargs
) -> Dict:
    """
    Fonction principale : analyse une offre d'emploi complète.
    
    Args:
        titre: Titre du poste
        description: Description du poste
        **kwargs: Autres informations optionnelles
        
    Returns:
        Dict: Offre structurée en JSON
    """
    try:
        # Construire le texte de l'offre
        texte_offre = f"""
TITRE DU POSTE : {titre}

DESCRIPTION :
{description}
"""
        
        # Ajouter les informations supplémentaires si disponibles
        if 'missions' in kwargs:
            texte_offre += f"\n\nMISSIONS :\n{kwargs['missions']}"
        
        if 'localisation' in kwargs:
            texte_offre += f"\n\nLOCALISATION : {kwargs['localisation']}"
        
        if 'type_contrat' in kwargs:
            texte_offre += f"\n\nTYPE DE CONTRAT : {kwargs['type_contrat']}"
        
        if 'salaire_min' in kwargs or 'salaire_max' in kwargs:
            salaire_info = f"\n\nSALAIRE : "
            if 'salaire_min' in kwargs:
                salaire_info += f"à partir de {kwargs['salaire_min']}€"
            if 'salaire_max' in kwargs:
                salaire_info += f" jusqu'à {kwargs['salaire_max']}€"
            texte_offre += salaire_info
        
        print("📄 Analyse de l'offre d'emploi...")
        offre_json = analyser_offre_texte(texte_offre)
        
        print("✅ Analyse terminée !")
        
        return offre_json
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return structure_offre_vide()


def structure_offre_vide() -> Dict:
    """Retourne une structure d'offre vide."""
    return {
        "titre": "",
        "description": "",
        "competences_requises": [],
        "experience_requise_ans": 0,
        "niveau_etudes_requis": 0,
        "langues_requises": [],
        "missions": None,
        "localisation": None,
        "type_contrat": None,
        "salaire_min": None,
        "salaire_max": None
    }


# ============================================
# FONCTION POUR SAUVEGARDER EN BASE DE DONNÉES
# ============================================

def creer_offre_en_base(
    db_session,
    recruteur_id: str,
    titre: str,
    description: str,
    json_structure: Dict,
    **kwargs
):
    """
    Crée un enregistrement offre d'emploi en base de données.
    
    Args:
        db_session: Session SQLAlchemy
        recruteur_id: UUID du recruteur
        titre: Titre du poste
        description: Description du poste
        json_structure: Structure JSON de l'offre
        **kwargs: Autres champs optionnels
        
    Returns:
        OffreEmploi: Instance du modèle OffreEmploi créé
    """
    from app.models.offre_emploi import OffreEmploi
    
    try:
        nouvelle_offre = OffreEmploi(
            recruteur_id=recruteur_id,
            titre=titre,
            description=description,
            json_structure=json_structure,
            localisation=kwargs.get('localisation'),
            type_contrat=kwargs.get('type_contrat'),
            salaire_min=kwargs.get('salaire_min'),
            salaire_max=kwargs.get('salaire_max'),
            experience_requise=json_structure.get('experience_requise_ans', 0),
            statut='ouverte'
        )
        
        db_session.add(nouvelle_offre)
        db_session.commit()
        db_session.refresh(nouvelle_offre)
        
        print(f"✅ Offre enregistrée en base de données (ID: {nouvelle_offre.id})")
        return nouvelle_offre
    
    except Exception as e:
        db_session.rollback()
        print(f"❌ Erreur lors de l'enregistrement en base: {e}")
        raise


# ============================================
# GÉNÉRATION D'EMBEDDING POUR L'OFFRE
# ============================================

def generer_embedding_offre(offre_json: Dict) -> List[float]:
    """
    Génère l'embedding pour une offre d'emploi.
    Utilise le module embeddings.py
    
    Args:
        offre_json: Structure JSON de l'offre
        
    Returns:
        List[float]: Vecteur d'embedding
    """
    from app.ai.embeddings import embed_text
    
    # Construire le texte représentatif de l'offre
    parties = []
    
    # Titre
    if offre_json.get("titre"):
        parties.append(f"Poste : {offre_json['titre']}")
    
    # Description
    if offre_json.get("description"):
        parties.append(offre_json['description'])
    
    # Compétences requises
    if offre_json.get("competences_requises"):
        parties.append("Compétences : " + ", ".join(offre_json['competences_requises']))
    
    # Missions (peut être string ou liste)
    if offre_json.get("missions"):
        missions = offre_json['missions']
        if isinstance(missions, list):
            parties.append("Missions : " + ", ".join(missions))
        else:
            parties.append(f"Missions : {missions}")
    
    # Langues (peut être liste de strings ou liste de dicts)
    if offre_json.get("langues_requises"):
        langues = offre_json['langues_requises']
        if langues:
            # Vérifier si c'est une liste de dictionnaires ou de strings
            if isinstance(langues[0], dict):
                # Format: [{"langue": "Français", "niveau": "courant"}]
                langues_str = []
                for l in langues:
                    langue_nom = l.get('langue', '')
                    niveau = l.get('niveau', '')
                    if langue_nom:
                        if niveau:
                            langues_str.append(f"{langue_nom} ({niveau})")
                        else:
                            langues_str.append(langue_nom)
                if langues_str:
                    parties.append("Langues : " + ", ".join(langues_str))
            else:
                # Format simple: ["Français", "Anglais"]
                parties.append("Langues : " + ", ".join(str(l) for l in langues))
    
    # Localisation
    if offre_json.get("localisation"):
        parties.append(f"Localisation : {offre_json['localisation']}")
    
    texte_offre = " | ".join(parties)
    
    print(f"📊 Génération de l'embedding pour l'offre...")
    print(f"📝 Texte à embedder : {texte_offre[:200]}...")
    
    embedding = embed_text(texte_offre)
    print(f"✅ Embedding généré ({len(embedding)} dimensions)")
    
    return embedding


# ============================================
# TEST EN LIGNE DE COMMANDE
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TEST D'ANALYSE OFFRE D'EMPLOI - LANGCHAIN")
    print("=" * 70)
    print()
    
    # Exemple d'offre
    offre_test = {
        "titre": "Développeur Full Stack Senior",
        "description": """
Nous recherchons un Développeur Full Stack Senior passionné pour rejoindre notre équipe dynamique.

Vous travaillerez sur des projets innovants utilisant les dernières technologies web.

Compétences requises :
- Python (Django, FastAPI)
- JavaScript (React, Node.js)
- PostgreSQL
- Docker
- Git

Minimum 5 ans d'expérience en développement web.
Diplôme Master en Informatique ou équivalent.

Langues : Français courant, Anglais professionnel

Localisation : Paris, France
Type de contrat : CDI
Salaire : 50000-65000€ brut annuel
        """,
        "missions": "Développement de nouvelles fonctionnalités, architecture logicielle, mentorat d'équipe",
        "localisation": "Paris, France",
        "type_contrat": "CDI",
        "salaire_min": 50000,
        "salaire_max": 65000
    }
    
    # Analyser l'offre
    resultat = analyser_offre_complete(**offre_test)
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTAT DE L'EXTRACTION")
    print("=" * 70)
    print(json.dumps(resultat, indent=2, ensure_ascii=False))
    print("\n" + "=" * 70)
    
    # Générer l'embedding
    try:
        embedding = generer_embedding_offre(resultat)
        print(f"📊 Embedding généré : {len(embedding)} dimensions")
        print(f"📊 Premiers éléments : {embedding[:5]}")
    except Exception as e:
        print(f"⚠️ Erreur génération embedding : {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)