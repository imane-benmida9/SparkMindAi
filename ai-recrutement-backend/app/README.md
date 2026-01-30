
🚀 AI Recruitment – Backend (FastAPI)

Backend du projet AI Recruitment, une plateforme intelligente de recrutement basée sur l’IA.
Ce backend fournit une API REST sécurisée pour la gestion des utilisateurs, CV, offres d’emploi et matching.

🧱 Stack Technique

Python 3.10+

FastAPI

PostgreSQL

Docker

SQLAlchemy

JWT (Authentification)

Passlib + bcrypt

ChromaDB (prévu pour le vector store / IA)

📁 Structure du projet
ai-recrutement-backend/
│
├── app/
│   ├── main.py                # Point d’entrée FastAPI
│   ├── api/                   # Routes (auth, candidats, offres, etc.)
│   ├── core/                  # Config, DB, sécurité, schéma SQL
│   ├── models/                # Modèles SQLAlchemy
│   ├── schemas/               # Schémas Pydantic
│   ├── services/              # Logique métier
│   ├── ai/                    # Modules IA (analyse CV, matching)
│   ├── vector_store/          # ChromaDB
│   └── utils/                 # Outils (logging, scoring)
│
├── requirements.txt
├── .gitignore
└── README.md

✅ Prérequis

Avant de commencer, assure-toi d’avoir installé :

Python 3.10 ou plus

Docker Desktop (v4.57.0 ou proche)

Git

Vérification :

python --version
docker --version
git --version

🐳 1. Lancer PostgreSQL avec Docker
1️⃣ Démarrer Docker Desktop

Assure-toi que Docker est bien lancé (icône verte).

2️⃣ Créer le container PostgreSQL
docker run --name pg-ai \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_recrutement \
  -p 5432:5432 \
  -d postgres:15


Vérification :

docker ps

🗄️ 2. Initialiser la base de données

Créer les tables à partir du schéma SQL.

Depuis la racine du projet :

type app\core\schema.sql | docker exec -i pg-ai psql -U postgres -d ai_recrutement


Vérifier les tables :

docker exec -it pg-ai psql -U postgres -d ai_recrutement -c "\dt"

🐍 3. Installer le backend FastAPI
1️⃣ Créer et activer un environnement virtuel
python -m venv venv
venv\Scripts\activate

2️⃣ Installer les dépendances
pip install -r requirements.txt


⚠️ Important (compatibilité auth) :

pip install bcrypt==4.0.1

⚙️ 4. Configuration .env

Créer un fichier .env à la racine du projet :

DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ai_recrutement
JWT_SECRET=dev_secret_123
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:8501,http://localhost:3000
APP_NAME=AI Recruitment API
ENV=dev


⚠️ Le fichier .env est ignoré par Git.

🚀 5. Lancer l’API
uvicorn app.main:app --reload


Si tout est correct :

Uvicorn running on http://127.0.0.1:8000

🧪 6. Tester l’API (Swagger)
Swagger UI

👉 http://127.0.0.1:8000/docs

Health check
GET /health


Réponse attendue :

{ "status": "ok" }

Authentification – ordre recommandé
1️⃣ Register
POST /api/auth/register


Body :

{
  "email": "test@example.com",
  "password": "123456",
  "role": "candidat"
}

2️⃣ Login
POST /api/auth/login


Copier le access_token.

3️⃣ Tester une route protégée

Cliquer sur Authorize dans Swagger :

Bearer <ACCESS_TOKEN>


Puis :

GET /api/auth/me

### CV (candidat authentifié)
- POST /cvs/upload — Upload PDF, analyse IA, sauvegarde BDD + index Chroma
- GET /cvs/my-cvs — Liste des CVs du candidat
- GET /cvs/{id} — Détail d’un CV
- DELETE /cvs/{id} — Supprimer un CV
- POST /cvs/index — Indexer un CV dans Chroma
- POST /cvs/search-offres — Recherche sémantique d’offres pour un CV

### Offres
- GET /offres — Liste des offres (pagination, filtre statut/localisation), public
- GET /offres/{id} — Détail d’une offre, public
- POST /offres — Créer une offre (recruteur)
- POST /offres/index — Indexer une offre dans Chroma
- POST /offres/search-cvs — Recherche sémantique de CVs pour une offre

### Candidats
- GET /candidats/me — Profil du candidat connecté
- GET /candidats/me/cvs — Liste des CVs du candidat (alias de /cvs/my-cvs)
- GET /candidats/{id}/cvs — Liste des CVs (candidat : uniquement les siens si id=me/current)

### Candidatures
- POST /candidatures — Postuler (offre_id, cv_id), calcule score + explication IA
- GET /candidatures — Mes candidatures (candidat) ou candidatures d’une offre (recruteur, ?offre_id=)
- GET /candidatures/{id} — Détail d’une candidature

### Matching
- POST /matching/score — Score 1 CV vs 1 offre (cv_id, offre_id)
- POST /matching/search-offres — Meilleures offres pour un CV (cv_id, top_k)
- POST /matching/search-candidats/{offre_id} — Meilleurs candidats pour une offre
- POST /matching/match — Compat frontend (body: candidate, job)
- POST /matching/test — Test avec cv_json et offre_json directs

🔐 Sécurité

Hash des mots de passe avec bcrypt

Authentification JWT

Rôles : candidat, recruteur, admin

Dépendances FastAPI pour la protection des routes

#pour la partie d'analyse de cv 
 il faut installer  ça "pip install fastapi uvicorn requests python-dotenv PyPDF2 python-multipart langchain langchain-groq "
 pour le fichier json  est dans e dossier cv_extraits
 j'ai   fait un fichier pour tester s'appele test_cv_upload pour le tester il faut  faire :
 1-cd app
 2-python test_cv_upload.py
 puis aller dans le navigateur et taper  http://localhost:8000 puis tester avec un cv sous format pdf



## Vector Store & Recherche Sémantique (Membre 4)

Cette partie du backend implémente le **vector store** du projet AI Recruitment.
Elle permet d’effectuer une **recherche sémantique CV ↔ Offres** à l’aide d’**embeddings** et de **ChromaDB**, afin de fournir une shortlist pertinente au module de matching.
### Objectifs

* Transformer les **CV** et **offres d’emploi** en représentations vectorielles
* Stocker ces vecteurs dans une base vectorielle persistante
* Rechercher les documents les plus similaires (Top-K)
* Exposer ces fonctionnalités via une API FastAPI
* Servir de base au module de **matching & explication** (Membre 5)

### ⚙️ Technologies utilisées

* **ChromaDB** – Base de données vectorielle locale
* **Embeddings ONNX** : `all-MiniLM-L6-v2`
* FastAPI
* Stockage persistant sur disque (pas de dépendance cloud)

> Aucun appel à une API externe pour les embeddings
> ➜ fonctionnement 100 % local


### 📁 Fichiers concernés

```text
app/vector_store/
 ├── chroma_client.py        # Initialisation du client Chroma
 ├── text_builders.py        # Conversion JSON → texte
 ├── indexing.py             # Indexation et recherche sémantique
 └── test_full_pipeline.py   # Test end-to-end sans API
```

Les données vectorielles sont persistées automatiquement dans :

```text
chroma_data/
```

---

### Configuration (.env)

Ajouter ou vérifier les variables suivantes :

```env
# --- CHROMA ---
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION_CVS=cvs
CHROMA_COLLECTION_OFFRES=offres
``

### 📦 Installation spécifique

```bash
pip install chromadb
```

⚠️ Lors du premier lancement, le modèle d’embeddings (`~80 MB`) est téléchargé automatiquement.

### Lancer l’API

```bash
uvicorn app.main:app --reload --port 8000
```

Documentation Swagger :

```
http://127.0.0.1:8000/docs
```

---

### Endpoints exposés

#### CVs

* `POST /cvs/index`
  Indexer un CV (JSON analysé)
* `POST /cvs/search-offres`
  Rechercher les offres les plus pertinentes pour un CV

#### Offres

* `POST /offres/index`
  Indexer une offre d’emploi
* `POST /offres/search-cvs`
  Rechercher les CV les plus pertinents pour une offre

---

### 🧪 Test local (sans passer par l’API)

Depuis la racine du projet :

```bash
python -m app.vector_store.test_full_pipeline
```

Ce test :

* indexe plusieurs CV et offres
* génère les embeddings
* effectue une recherche Top-K
* affiche les résultats de similarité

---

### 🧠 Notes techniques

* Les **embeddings** fonctionnent sur du **texte**, pas sur du JSON structuré
  ➜ les CV et offres sont convertis en texte avant vectorisation.
* ChromaDB agit comme une **mémoire sémantique**, pas comme un moteur d’IA générative.
* Le calcul du score final et l’explication IA sont réalisés dans le module de **matching** (Membre 5).


