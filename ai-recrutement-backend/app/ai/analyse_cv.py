"""
Agent d'analyse de CV par IA générative avec LangChain.
Membre 3 - Niveau 1 & 2
- Sauvegarde du PDF dans uploads/cvs/
- Stockage du JSON en base de données
"""

import os
import json
import shutil
from typing import Dict, Optional
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO
from datetime import datetime
from pathlib import Path

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


# Charger les variables d'environnement
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Dossier pour stocker les PDF uploadés
UPLOAD_DIR = Path("uploads/cvs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# SCHÉMA PYDANTIC POUR VALIDATION
# ============================================

class Experience(BaseModel):
    """Modèle d'une expérience professionnelle"""
    poste: str = Field(description="Titre du poste")
    entreprise: Optional[str] = Field(description="Nom de l'entreprise")
    periode: Optional[str] = Field(description="Période de travail")
    description: Optional[str] = Field(description="Description des responsabilités")


class Formation(BaseModel):
    """Modèle d'une formation"""
    diplome: str = Field(description="Nom du diplôme")
    etablissement: Optional[str] = Field(description="Nom de l'établissement")
    annee: Optional[str] = Field(description="Année d'obtention")


class CVStructure(BaseModel):
    """Schéma complet d'un CV"""
    nom: Optional[str] = Field(description="Nom complet du candidat")
    email: Optional[str] = Field(description="Adresse email")
    telephone: Optional[str] = Field(description="Numéro de téléphone")
    competences: list[str] = Field(default=[], description="Liste des compétences")
    experiences: list[Experience] = Field(default=[], description="Expériences professionnelles")
    formations: list[Formation] = Field(default=[], description="Formations académiques")
    langues: list[str] = Field(default=[], description="Langues parlées")


# ============================================
# PROMPT LANGCHAIN
# ============================================

PROMPT_TEMPLATE = """
Tu es un expert en analyse de CV. Ta mission est d'extraire TOUTES les informations d'un CV et de les structurer en JSON.

RÈGLES IMPORTANTES :
1. Extrais TOUTES les compétences mentionnées (techniques, langages, outils, soft skills)
2. Pour chaque expérience, inclus TOUS les détails disponibles
3. Pour les langues, précise le niveau si mentionné
4. Si une information n'est pas présente, utilise null ou une liste vide []
5. Sois exhaustif et précis

STRUCTURE ATTENDUE :
- nom: Nom complet du candidat
- email: Adresse email
- telephone: Numéro de téléphone avec indicatif
- competences: Liste de toutes les compétences
- experiences: Liste des expériences avec poste, entreprise, periode, description
- formations: Liste des formations avec diplome, etablissement, annee
- langues: Liste des langues avec niveau si disponible

CV À ANALYSER :
{cv_text}

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


def creer_chaine_extraction():
    """Crée la chaîne LangChain pour l'extraction de CV"""
    parser = JsonOutputParser(pydantic_object=CVStructure)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = initialiser_llm()
    chain = prompt | llm | parser
    return chain


# ============================================
# FONCTIONS D'EXTRACTION
# ============================================

def extraire_texte_pdf(fichier_pdf: bytes) -> str:
    """
    Extrait le texte brut d'un fichier PDF.
    
    Args:
        fichier_pdf: Contenu binaire du PDF
        
    Returns:
        str: Texte extrait du PDF
    """
    try:
        pdf_file = BytesIO(fichier_pdf)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        texte_complet = ""
        for page in pdf_reader.pages:
            texte_complet += page.extract_text() + "\n"
        
        if not texte_complet.strip():
            raise ValueError("Le PDF ne contient pas de texte extractible")
        
        print(f"✅ Texte extrait du PDF ({len(texte_complet)} caractères)")
        return texte_complet.strip()
    
    except Exception as e:
        print(f"❌ Erreur extraction PDF: {e}")
        raise


def extraire_cv_texte(texte_cv: str) -> Dict:
    """
    Analyse un CV texte avec LangChain et retourne un JSON structuré.
    
    Args:
        texte_cv: Contenu texte du CV
        
    Returns:
        dict: CV structuré selon CVStructure
    """
    try:
        print("🔄 Création de la chaîne LangChain...")
        chain = creer_chaine_extraction()
        
        print("🤖 Envoi à Groq via LangChain...")
        resultat = chain.invoke({"cv_text": texte_cv})
        
        print("✅ Réponse reçue et parsée")
        return resultat
    
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse LangChain: {str(e)}")
        return structure_cv_vide()


def sauvegarder_fichier_pdf(fichier_pdf: bytes, nom_fichier: str) -> str:
    """
    Sauvegarde le fichier PDF dans le dossier uploads/cvs/.
    
    Args:
        fichier_pdf: Contenu binaire du PDF
        nom_fichier: Nom du fichier original
        
    Returns:
        str: Chemin relatif du fichier sauvegardé
    """
    try:
        # Créer un nom unique avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_base = Path(nom_fichier).stem  # Nom sans extension
        extension = Path(nom_fichier).suffix  # .pdf
        
        nom_unique = f"{nom_base}_{timestamp}{extension}"
        chemin_complet = UPLOAD_DIR / nom_unique
        
        # Sauvegarder le fichier
        with open(chemin_complet, 'wb') as f:
            f.write(fichier_pdf)
        
        chemin_relatif = str(chemin_complet)
        print(f"💾 PDF sauvegardé : {chemin_relatif}")
        
        return chemin_relatif
    
    except Exception as e:
        print(f"❌ Erreur sauvegarde PDF: {e}")
        raise


def analyser_cv_pdf(
    fichier_pdf: bytes, 
    nom_fichier: str,
    sauvegarder_pdf: bool = True
) -> tuple[Dict, str, str]:
    """
    Fonction principale : analyse un PDF de CV complet avec LangChain.
    
    Args:
        fichier_pdf: Contenu binaire du fichier PDF
        nom_fichier: Nom du fichier original
        sauvegarder_pdf: Si True, sauvegarde le PDF localement
        
    Returns:
        tuple: (cv_json, texte_brut, chemin_pdf)
    """
    try:
        # Étape 1: Sauvegarder le PDF (si demandé)
        chemin_pdf = None
        if sauvegarder_pdf:
            print("💾 Sauvegarde du PDF...")
            chemin_pdf = sauvegarder_fichier_pdf(fichier_pdf, nom_fichier)
        
        # Étape 2: Extraction du texte
        print("📄 Extraction du texte du PDF...")
        texte_brut = extraire_texte_pdf(fichier_pdf)
        
        # Étape 3: Analyse par LangChain
        print("🤖 Analyse par LangChain + Groq...")
        cv_json = extraire_cv_texte(texte_brut)
        
        print("✅ Analyse terminée !")
        
        return cv_json, texte_brut, chemin_pdf
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return structure_cv_vide(), "", None


def structure_cv_vide() -> Dict:
    """Retourne une structure CV vide."""
    return {
        "nom": None,
        "email": None,
        "telephone": None,
        "competences": [],
        "experiences": [],
        "formations": [],
        "langues": []
    }


# ============================================
# FONCTION POUR SAUVEGARDER EN BASE DE DONNÉES
# ============================================

def creer_cv_en_base(
    db_session,
    candidat_id: str,
    fichier_nom: str,
    texte_brut: str,
    json_structure: Dict,
    fichier_chemin: str = None
):
    """
    Crée un enregistrement CV en base de données.
    
    Args:
        db_session: Session SQLAlchemy
        candidat_id: UUID du candidat
        fichier_nom: Nom du fichier PDF
        texte_brut: Texte extrait du PDF
        json_structure: Structure JSON du CV
        fichier_chemin: Chemin du fichier sauvegardé
        
    Returns:
        CV: Instance du modèle CV créé
    """
    from app.models.cv import CV
    
    try:
        import uuid
        nouveau_cv = CV(
            id=str(uuid.uuid4()),
            candidat_id=candidat_id,
            fichier_nom=fichier_nom,
            texte_brut=texte_brut,
            json_structure=json_structure
        )
        
        db_session.add(nouveau_cv)
        db_session.commit()
        db_session.refresh(nouveau_cv)
        
        print(f"✅ CV enregistré en base de données (ID: {nouveau_cv.id})")
        return nouveau_cv
    
    except Exception as e:
        db_session.rollback()
        print(f"❌ Erreur lors de l'enregistrement en base: {e}")
        raise


# ============================================
# TEST EN LIGNE DE COMMANDE
# ============================================
if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("🧪 TEST D'EXTRACTION CV PDF - LANGCHAIN")
    print("=" * 70)
    print()
    
    if len(sys.argv) > 1:
        chemin_pdf = sys.argv[1]
        
        try:
            with open(chemin_pdf, 'rb') as f:
                contenu_pdf = f.read()
            
            nom_fichier = os.path.basename(chemin_pdf)
            print(f"📂 Fichier: {nom_fichier}")
            print(f"📏 Taille: {len(contenu_pdf)} octets\n")
            
            # Analyser le CV
            cv_json, texte_brut, chemin_sauvegarde = analyser_cv_pdf(
                contenu_pdf, 
                nom_fichier,
                sauvegarder_pdf=True
            )
            
            print("\n" + "=" * 70)
            print("📊 RÉSULTAT DE L'EXTRACTION")
            print("=" * 70)
            print(json.dumps(cv_json, indent=2, ensure_ascii=False))
            print("\n" + "=" * 70)
            print(f"📁 PDF sauvegardé : {chemin_sauvegarde}")
            print(f"📝 Texte extrait : {len(texte_brut)} caractères")
            print("=" * 70)
            
        except FileNotFoundError:
            print(f"❌ Fichier introuvable: {chemin_pdf}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    else:
        print("⚠️  Usage: python analyse_cv.py chemin/vers/cv.pdf")