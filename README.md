AI Recruitment — Plateforme intelligente de recrutement

AI Recruitment est une plateforme web complète de recrutement assisté par Intelligence Artificielle, permettant d’analyser automatiquement des CV, de gérer des offres d’emploi et de réaliser un matching intelligent et explicable entre candidats et recruteurs.

Le projet repose sur une architecture full‑stack avec un backend FastAPI et un frontend React, et met l’accent sur la pertinence du matching, la transparence des scores et la sécurité des données.

🎯 Objectifs du projet

Automatiser l’analyse des CV (PDF) grâce à l’IA

Structurer les données extraites sous forme JSON

Comparer sémantiquement les profils candidats et les offres d’emploi

Calculer un score de compatibilité clair et justifié

Expliquer le résultat du matching de manière compréhensible

Offrir une expérience fluide aux candidats et recruteurs

🧱 Architecture globale
[ Frontend (React) ]
        ↓  REST API (JWT)
[ Backend FastAPI ]
        ↓
[ PostgreSQL ]   [ ChromaDB ]
        ↓             ↓
  Données métier   Embeddings sémantiques
        ↓
[ IA : Analyse CV • Matching • Explication ]
🗂️ Organisation du dépôt
ai-recruitment/
│
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ai/
│   │   ├── vector_store/
│   │   └── utils/
│   ├── chroma_data/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                # Application React
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── README.md
│
└── README.md                # README global
🧠 Fonctionnalités principales
👤 Authentification & sécurité

Inscription et connexion sécurisées

Authentification par JWT

Gestion des rôles : candidat, recruteur, admin

Protection des routes sensibles

📄 Gestion et analyse des CV

Upload de CV au format PDF

Extraction automatique du texte

Analyse par LLM (IA)

Structuration des données en JSON

Sauvegarde en base de données

🧾 Gestion des offres d’emploi

Création et modification d’offres

Consultation publique des offres

Filtrage et pagination

Indexation sémantique des offres

🔎 Matching intelligent

Génération d’embeddings pour CV et offres

Recherche sémantique via ChromaDB

Calcul d’un score de compatibilité

Combinaison règles métier + similarité vectorielle

💬 Explication du score

Génération d’une explication IA lisible

Mise en avant des points forts et écarts

Recommandations d’amélioration

🧠 Intelligence Artificielle

Le projet intègre plusieurs briques IA :

Analyse CV : extraction des compétences, expériences, diplômes

Embeddings : représentation vectorielle du contenu textuel

Matching : comparaison sémantique CV ↔ Offre

Explication : justification du score par LLM

Les embeddings sont calculés localement (pas d’API externe).

🗃️ Données & persistance

PostgreSQL : utilisateurs, CV, offres, candidatures

ChromaDB : stockage persistant des vecteurs

Séparation données métier / données sémantiques

🔐 Sécurité & bonnes pratiques

Hash des mots de passe avec bcrypt

Variables sensibles dans .env

CORS configuré

Validation des données (Pydantic)

Gestion centralisée des erreurs

🧪 Tests & validation

Tests locaux via scripts Python

Tests end‑to‑end (upload CV → matching)

Swagger UI pour validation API

🎨 Expérience utilisateur

Interfaces distinctes candidat / recruteur

Feedback clair (chargement, erreurs, succès)

Visualisation simple des scores et explications

📌 Démonstration attendue

Un candidat s’inscrit et upload son CV

Un recruteur crée une offre

Le système analyse et compare

Un score est généré

Une explication claire est affichée

 Conclusion

AI Recruitment est une solution complète et moderne de recrutement intelligent, combinant IA, recherche sémantique et architecture web robuste, avec un fort accent sur la transparence, la qualité du matching et la valeur métier.

Ce dépôt constitue une base solide pour une démonstration académique ou professionnelle.