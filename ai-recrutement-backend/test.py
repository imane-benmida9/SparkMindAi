"""
Exemple d'utilisation du système de matching avec embeddings et recherche vectorielle
"""

from app.ai.moteur_matching import executer_matching
from app.vector_store.indexing import index_cv_from_json, index_offer, search_cvs_for_offer, search_offres_for_cv
import json


# ============================================
# EXEMPLE 1 : Matching simple avec embeddings
# ============================================

def exemple_matching_simple():
    print("=" * 70)
    print("EXEMPLE 1 : MATCHING SIMPLE AVEC EMBEDDINGS")
    print("=" * 70)
    
    # CV candidat
    cv = {
        "nom": "Sarah Martin",
        "competences": ["Python", "Django", "PostgreSQL", "Git"],
        "experiences": [
            {
                "poste": "Développeur Python",
                "periode": "2020-2024",
                "description": "Développement web avec Django"
            }
        ],
        "formations": [
            {
                "diplome": "Licence Informatique",
                "annee": "2020"
            }
        ],
        "langues": ["Français", "Anglais"]
    }
    
    # Offre d'emploi
    offre = {
        "titre": "Développeur Backend Python",
        "description": "Développement d'applications web",
        "competences_requises": ["Python", "Django", "PostgreSQL"],
        "experience_requise_ans": 2,
        "niveau_etudes_requis": 3,
        "langues_requises": ["Français"]
    }
    
    # Indexer le CV et l'offre dans ChromaDB
    print("\n📚 Indexation dans ChromaDB...")
    index_cv_from_json("cv_sarah", cv, metadata={"nom": "Sarah Martin"})
    index_offer("offre_backend_python", offre, metadata={"titre": "Développeur Backend Python"})
    print("✅ Indexation terminée")
    
    # Exécuter le matching
    print("\n🔍 Exécution du matching...")
    resultat = executer_matching(
        cv_json=cv,
        offre_json=offre,
        generer_explications=True
    )
    
    # Afficher les résultats
    print(f"\n📊 Score final: {resultat['score_final']}%")
    print(f"🎯 Recommandation: {resultat['recommandation']}")
    
    print("\n💼 Explication pour le recruteur:")
    if resultat.get('explications'):
        recruteur = resultat['explications'].get('pour_recruteur', {})
        print(f"  Décision: {recruteur.get('recommandation', 'N/A')}")
        print(f"  Synthèse: {recruteur.get('synthese', 'N/A')}")
        
        if recruteur.get('points_forts'):
            print("\n  Points forts:")
            for pf in recruteur['points_forts']:
                print(f"    ✅ {pf}")
        
        if recruteur.get('points_faibles'):
            print("\n  Points faibles:")
            for pb in recruteur['points_faibles']:
                print(f"    ❌ {pb}")
    
    print("\n👤 Explication pour le candidat:")
    if resultat.get('explications'):
        candidat = resultat['explications'].get('pour_candidat', {})
        if candidat.get('message_principal'):
            print(f"  {candidat['message_principal']}")
        
        if candidat.get('conseils'):
            print("\n  Conseils:")
            for conseil in candidat['conseils']:
                print(f"    💡 {conseil}")
    
    return resultat


# ============================================
# EXEMPLE 2 : Recherche vectorielle CV pour offre
# ============================================

def exemple_recherche_vectorielle_cvs():
    print("\n" + "=" * 70)
    print("EXEMPLE 2 : RECHERCHE VECTORIELLE - CVS POUR UNE OFFRE")
    print("=" * 70)
    
    # Indexer plusieurs CVs
    cvs = [
        {
            "nom": "Ahmed Alami",
            "competences": ["JavaScript", "React", "Node.js", "MongoDB"],
            "experiences": [
                {
                    "poste": "Développeur Full Stack",
                    "periode": "2021-2024",
                    "description": "Applications web React/Node"
                }
            ],
            "formations": [
                {
                    "diplome": "Master Informatique",
                    "annee": "2021"
                }
            ],
            "langues": ["Français", "Anglais", "Arabe"]
        },
        {
            "nom": "Marie Dubois",
            "competences": ["Python", "Django", "PostgreSQL", "Docker"],
            "experiences": [
                {
                    "poste": "Développeur Backend",
                    "periode": "2019-2024",
                    "description": "API REST avec Django"
                }
            ],
            "formations": [
                {
                    "diplome": "Ingénieur Informatique",
                    "annee": "2019"
                }
            ],
            "langues": ["Français", "Anglais"]
        },
        {
            "nom": "Thomas Bernard",
            "competences": ["Java", "Spring", "MySQL", "Kubernetes"],
            "experiences": [
                {
                    "poste": "Développeur Java",
                    "periode": "2018-2024",
                    "description": "Applications entreprise avec Spring Boot"
                }
            ],
            "formations": [
                {
                    "diplome": "Master Informatique",
                    "annee": "2018"
                }
            ],
            "langues": ["Français"]
        }
    ]
    
    print("\n📚 Indexation des CVs...")
    for i, cv in enumerate(cvs):
        index_cv_from_json(f"cv_{i+1}", cv, metadata={"nom": cv["nom"]})
    print(f"✅ {len(cvs)} CVs indexés")
    
    # Offre à matcher
    offre = {
        "titre": "Développeur Backend Python Senior",
        "description": "Développement d'API REST avec Django et PostgreSQL",
        "competences_requises": ["Python", "Django", "PostgreSQL", "Docker"],
        "experience_requise_ans": 4,
        "niveau_etudes_requis": 4,
        "langues_requises": ["Français", "Anglais"]
    }
    
    print(f"\n🔍 Recherche des meilleurs CVs pour: {offre['titre']}")
    
    # Recherche vectorielle
    resultats = search_cvs_for_offer(offre, top_k=3)
    
    print("\n📊 Top 3 CVs trouvés:\n")
    if resultats and 'ids' in resultats and resultats['ids']:
        for i, (cv_id, distance, metadata) in enumerate(zip(
            resultats['ids'][0],
            resultats['distances'][0],
            resultats['metadatas'][0]
        )):
            similarity = 1 - distance  # Distance cosinus -> similarité
            print(f"{i+1}. {metadata.get('nom', cv_id)}")
            print(f"   Similarité: {similarity:.2%}")
            print(f"   Distance: {distance:.4f}\n")
    
    return resultats


# ============================================
# EXEMPLE 3 : Recherche vectorielle offres pour CV
# ============================================

def exemple_recherche_vectorielle_offres():
    print("\n" + "=" * 70)
    print("EXEMPLE 3 : RECHERCHE VECTORIELLE - OFFRES POUR UN CV")
    print("=" * 70)
    
    # CV du candidat
    cv = {
        "nom": "Sophie Laurent",
        "competences": ["React", "TypeScript", "Node.js", "GraphQL", "AWS"],
        "experiences": [
            {
                "poste": "Développeur Frontend Senior",
                "periode": "2019-2024",
                "description": "Applications React avec TypeScript et GraphQL"
            }
        ],
        "formations": [
            {
                "diplome": "Master Informatique",
                "annee": "2019"
            }
        ],
        "langues": ["Français", "Anglais"]
    }
    
    # Indexer plusieurs offres
    offres = [
        {
            "titre": "Développeur React Senior",
            "description": "Applications React avec TypeScript",
            "competences_requises": ["React", "TypeScript", "Redux"],
            "experience_requise_ans": 3,
            "niveau_etudes_requis": 4,
            "langues_requises": ["Français", "Anglais"]
        },
        {
            "titre": "Développeur Full Stack",
            "description": "Stack moderne React/Node.js/GraphQL",
            "competences_requises": ["React", "Node.js", "GraphQL", "MongoDB"],
            "experience_requise_ans": 4,
            "niveau_etudes_requis": 4,
            "langues_requises": ["Français"]
        },
        {
            "titre": "Développeur Backend Python",
            "description": "API REST Django PostgreSQL",
            "competences_requises": ["Python", "Django", "PostgreSQL"],
            "experience_requise_ans": 3,
            "niveau_etudes_requis": 3,
            "langues_requises": ["Français"]
        }
    ]
    
    print("\n📚 Indexation des offres...")
    for i, offre in enumerate(offres):
        index_offer(f"offre_{i+1}", offre, metadata={"titre": offre["titre"]})
    print(f"✅ {len(offres)} offres indexées")
    
    print(f"\n🔍 Recherche des meilleures offres pour: {cv['nom']}")
    
    # Recherche vectorielle
    resultats = search_offres_for_cv(cv, top_k=3)
    
    print("\n📊 Top 3 offres trouvées:\n")
    if resultats and 'ids' in resultats and resultats['ids']:
        for i, (offre_id, distance, metadata) in enumerate(zip(
            resultats['ids'][0],
            resultats['distances'][0],
            resultats['metadatas'][0]
        )):
            similarity = 1 - distance
            print(f"{i+1}. {metadata.get('titre', offre_id)}")
            print(f"   Similarité: {similarity:.2%}")
            print(f"   Distance: {distance:.4f}\n")
    
    return resultats


# ============================================
# EXEMPLE 4 : Comparaison avec et sans embeddings
# ============================================

def exemple_comparaison_offres():
    print("\n" + "=" * 70)
    print("EXEMPLE 4 : COMPARAISON MATCHING DIRECT VS VECTORIEL")
    print("=" * 70)
    
    cv = {
        "nom": "Ahmed Alami",
        "competences": ["JavaScript", "React", "Node.js", "MongoDB"],
        "experiences": [
            {
                "poste": "Développeur Full Stack",
                "periode": "2021-2024",
                "description": "Applications web React/Node"
            }
        ],
        "formations": [
            {
                "diplome": "Master Informatique",
                "annee": "2021"
            }
        ],
        "langues": ["Français", "Anglais", "Arabe"]
    }
    
    offres = [
        {
            "titre": "Développeur React Senior",
            "competences_requises": ["React", "JavaScript", "TypeScript"],
            "experience_requise_ans": 3,
            "niveau_etudes_requis": 4,
            "langues_requises": ["Français", "Anglais"]
        },
        {
            "titre": "Développeur Full Stack",
            "competences_requises": ["React", "Node.js", "MongoDB"],
            "experience_requise_ans": 2,
            "niveau_etudes_requis": 3,
            "langues_requises": ["Français"]
        },
        {
            "titre": "Développeur Backend Python",
            "competences_requises": ["Python", "Django", "PostgreSQL"],
            "experience_requise_ans": 3,
            "niveau_etudes_requis": 4,
            "langues_requises": ["Français"]
        }
    ]
    
    # Indexer les offres
    print("\n📚 Indexation des offres dans ChromaDB...")
    for i, offre in enumerate(offres):
        index_offer(f"offre_comp_{i+1}", offre, metadata={"titre": offre["titre"]})
    
    # 1. Matching direct (sans recherche vectorielle)
    print("\n🔷 MATCHING DIRECT (algorithme de scoring)")
    resultats_direct = []
    
    for offre in offres:
        resultat = executer_matching(
            cv_json=cv,
            offre_json=offre,
            generer_explications=False
        )
        resultats_direct.append({
            "offre": offre["titre"],
            "score": resultat["score_final"],
            "recommandation": resultat["recommandation"]
        })
    
    resultats_direct.sort(key=lambda x: x["score"], reverse=True)
    
    print("\n📊 Classement par matching direct:\n")
    for i, r in enumerate(resultats_direct, 1):
        print(f"{i}. {r['offre']}")
        print(f"   Score: {r['score']}% - {r['recommandation']}\n")
    
    # 2. Recherche vectorielle
    print("\n🔶 RECHERCHE VECTORIELLE (similarité sémantique)")
    resultats_vectoriel = search_offres_for_cv(cv, top_k=3)
    
    print("\n📊 Classement par recherche vectorielle:\n")
    if resultats_vectoriel and 'ids' in resultats_vectoriel and resultats_vectoriel['ids']:
        for i, (offre_id, distance, metadata) in enumerate(zip(
            resultats_vectoriel['ids'][0],
            resultats_vectoriel['distances'][0],
            resultats_vectoriel['metadatas'][0]
        )):
            similarity = (1 - distance) * 100
            print(f"{i+1}. {metadata.get('titre', offre_id)}")
            print(f"   Similarité: {similarity:.1f}%\n")
    
    return resultats_direct, resultats_vectoriel


# ============================================
# EXEMPLE 5 : Export JSON
# ============================================

def exemple_export_json():
    print("\n" + "=" * 70)
    print("EXEMPLE 5 : EXPORT JSON AVEC EMBEDDINGS")
    print("=" * 70)
    
    cv = {
        "nom": "Test User",
        "competences": ["Python", "FastAPI"],
        "experiences": [],
        "formations": [],
        "langues": ["Français"]
    }
    
    offre = {
        "titre": "Développeur Python Junior",
        "competences_requises": ["Python"],
        "experience_requise_ans": 0,
        "niveau_etudes_requis": 3,
        "langues_requises": ["Français"]
    }
    
    # Indexer
    index_cv_from_json("cv_test_export", cv, metadata={"nom": "Test User"})
    index_offer("offre_test_export", offre, metadata={"titre": "Développeur Python Junior"})
    
    # Matching
    resultat = executer_matching(cv, offre, generer_explications=True)
    
    # Recherche vectorielle
    recherche = search_cvs_for_offer(offre, top_k=1)
    
    # Créer un rapport complet
    rapport = {
        "matching_direct": resultat,
        "recherche_vectorielle": {
            "cv_id": recherche['ids'][0][0] if recherche['ids'] else None,
            "distance": float(recherche['distances'][0][0]) if recherche['distances'] else None,
            "similarite": float(1 - recherche['distances'][0][0]) if recherche['distances'] else None
        }
    }
    
    # Sauvegarder en JSON
    filename = "app/cv_extraits/matching_result_with_embeddings.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Rapport exporté vers: {filename}")
    print(f"📄 Taille: {len(json.dumps(rapport))} caractères")
    
    return rapport


# ============================================
# EXÉCUTION
# ============================================

if __name__ == "__main__":
    print("\n🚀 EXEMPLES D'UTILISATION DU SYSTÈME DE MATCHING AVEC EMBEDDINGS\n")
    
    try:
        # Exemple 1
        print("\n▶️  Exécution Exemple 1...")
        exemple_matching_simple()
        
        # Exemple 2
        print("\n▶️  Exécution Exemple 2...")
        exemple_recherche_vectorielle_cvs()
        
        # Exemple 3
        print("\n▶️  Exécution Exemple 3...")
        exemple_recherche_vectorielle_offres()
        
        # Exemple 4
        print("\n▶️  Exécution Exemple 4...")
        exemple_comparaison_offres()
        
        # Exemple 5
        print("\n▶️  Exécution Exemple 5...")
        exemple_export_json()
        
        print("\n" + "=" * 70)
        print("✅ TOUS LES EXEMPLES TERMINÉS AVEC SUCCÈS")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()