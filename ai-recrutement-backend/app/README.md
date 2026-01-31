AI Recruitment — Backend (FastAPI)

Backend du projet AI Recruitment, une plateforme intelligente de recrutement basée sur l’IA. Ce service expose une API REST sécurisée permettant la gestion des utilisateurs, CV, offres d’emploi, candidatures et du matching intelligent CV ↔ Offres.

🎯 Objectifs du backend

Fournir une API robuste et sécurisée

Centraliser la logique métier du recrutement

Analyser automatiquement les CV via IA

Réaliser un matching sémantique et explicable

Servir de socle au frontend (SPA)

🧱 Stack technique

Python 3.10+

FastAPI

PostgreSQL

SQLAlchemy + Alembic

JWT (authentification)

Passlib + bcrypt (hashing)

ChromaDB (vector store)

LangChain (orchestration IA)

Docker (services externes)

📁 Structure du projet
ai-recruitment-backend/
│
├── app/
│   ├── main.py                # Point d’entrée FastAPI
│   ├── api/                   # Routes (auth, cvs, offres, matching…)
│   ├── core/                  # Config, sécurité, DB
│   ├── models/                # Modèles SQLAlchemy
│   ├── schemas/               # Schémas Pydantic
│   ├── services/              # Logique métier
│   ├── ai/                    # Analyse CV, prompts, matching
│   ├── vector_store/          # ChromaDB & embeddings
│   ├── utils/                 # Helpers (logging, scoring)
│   └── tests/                 # Scripts de test locaux
│
├── chroma_data/               # Données vectorielles persistées
├── requirements.txt
├── .env.example
└── README.md
✅ Prérequis

Python 3.10+

Docker Desktop

Git

Vérification :

python --version
docker --version
git --version
🐳 Lancer PostgreSQL avec Docker
docker run --name pg-ai \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_recrutement \
  -p 5432:5432 \
  -d postgres:15

Vérification :

docker ps
🐍 Installation du backend
1. Environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
2. Dépendances
pip install -r requirements.txt
pip install bcrypt==4.0.1
⚙️ Configuration (.env)

Créer un fichier .env à la racine :

DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ai_recrutement
JWT_SECRET=dev_secret_123
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
APP_NAME=AI Recruitment API
ENV=dev


# --- CHROMA ---
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION_CVS=cvs
CHROMA_COLLECTION_OFFRES=offres

⚠️ Le fichier .env est ignoré par Git.

🚀 Lancer l’API
uvicorn app.main:app --reload

API : http://127.0.0.1:8000

Swagger : http://127.0.0.1:8000/docs

🔐 Authentification

Hash des mots de passe avec bcrypt

Authentification JWT

Rôles : candidat, recruteur, admin

Parcours recommandé (Swagger)

POST /api/auth/register

POST /api/auth/login

Authorize → Bearer <ACCESS_TOKEN>

GET /api/auth/me

📄 Gestion des CV

POST /cvs/upload — Upload PDF, analyse IA, sauvegarde DB + Chroma

GET /cvs/my-cvs — Liste des CVs du candidat

GET /cvs/{id} — Détail d’un CV

DELETE /cvs/{id} — Supprimer un CV

POST /cvs/index — Indexation Chroma

POST /cvs/search-offres — Recherche sémantique d’offres

🧾 Offres d’emploi

GET /offres — Liste publique (filtres, pagination)

GET /offres/{id} — Détail offre

POST /offres — Création (recruteur)

POST /offres/index — Indexation Chroma

POST /offres/search-cvs — Recherche sémantique de CVs

🧠 Matching & Candidatures

POST /candidatures — Postuler (score + explication IA)

GET /candidatures — Liste (candidat / recruteur)

GET /candidatures/{id} — Détail candidature

POST /matching/score — Score CV vs Offre

POST /matching/search-offres

POST /matching/search-candidats/{offre_id}

📑 Analyse de CV (IA)
Dépendances spécifiques
pip install fastapi uvicorn requests python-dotenv PyPDF2 python-multipart langchain langchain-groq

Les JSON extraits sont stockés dans cv_extraits/

Script de test : test_cv_upload.py

Test local
cd app
python test_cv_upload.py

Puis ouvrir : http://localhost:8000

🧠 Vector Store & Recherche Sémantique

ChromaDB (local, persistant)

Embeddings ONNX : all-MiniLM-L6-v2

Aucun appel externe

app/vector_store/
 ├── chroma_client.py
 ├── text_builders.py
 ├── indexing.py
 └── test_full_pipeline.py

Test local :

python -m app.vector_store.test_full_pipeline
📝 Notes techniques

Les embeddings fonctionnent sur du texte (JSON → texte)

ChromaDB = mémoire sémantique

Le scoring final combine règles métier + similarité

L’explication est générée par IA (LLM)