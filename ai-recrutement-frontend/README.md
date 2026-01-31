AI Recruitment — Frontend

Frontend du projet AI Recruitment, une application web permettant aux candidats et recruteurs d’interagir avec la plateforme de recrutement assistée par IA.

🎯 Objectifs du frontend

Offrir une interface claire et intuitive

Permettre l’authentification sécurisée

Faciliter l’upload et la gestion des CV

Créer et consulter des offres d’emploi

Visualiser les scores de matching et leurs explications

🧱 Stack technique

React

TypeScript

Vite

Axios (API REST)

React Router

JWT (Bearer Token)

CSS / Tailwind / MUI (selon implémentation)

📁 Structure du projet
ai-recruitment-frontend/
│
├── src/
│   ├── api/            # Appels API backend
│   ├── auth/           # Gestion auth & tokens
│   ├── components/     # Composants UI réutilisables
│   ├── pages/          # Pages (Login, Dashboard, CV, Offres)
│   ├── routes/         # Routing
│   ├── services/       # Logique métier frontend
│   ├── types/          # Types TypeScript
│   └── utils/          # Helpers
│
├── public/
├── .env
├── package.json
└── README.md
✅ Prérequis

Node.js 18+

npm ou yarn

node --version
npm --version
⚙️ Configuration (.env)

Créer un fichier .env :

VITE_API_URL=http://127.0.0.1:8000
📦 Installation
npm install
# ou
yarn install
🚀 Lancer l’application
npm run dev

Application disponible sur :

http://localhost:5173
🔐 Authentification

Login / Register

Stockage du token JWT (localStorage)

Intercepteur Axios pour Authorization Header

Authorization: Bearer <token>
📄 Fonctionnalités principales
Candidat

Création de compte

Upload de CV (PDF)

Liste et détail des CV

Consultation des offres

Postuler à une offre

Visualisation du score et de l’explication IA

Recruteur

Création de compte

Création et gestion des offres

Consultation des candidatures

Visualisation des meilleurs profils

🔗 Communication avec le backend

API REST via Axios

Gestion des erreurs globales

Loading & feedback utilisateur

🧪 Tests & validation

Vérification formulaires

Gestion erreurs API

Cas token expiré

Upload fichiers volumineux

🎨 UX / UI

Interfaces simples et orientées métier

Feedback clair (loading, erreurs, succès)

Séparation candidat / recruteur