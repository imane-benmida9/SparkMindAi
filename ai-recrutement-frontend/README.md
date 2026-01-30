# AI Recruitment – Frontend

Interface React (Vite) pour la plateforme AI Recruitment. Design inspiré des maquettes type [AI Recruitment Platform (Figma)](https://www.figma.com/make/TEBr3znflDQpL0l7VhELUn/AI-Recruitment-Platform).

## Stack

- **React 19** + **Vite 7**
- **React Router DOM** (routes protégées, auth)
- **Axios** (API + JWT)

## Prérequis

- Node.js 18+
- Backend API démarré sur `http://localhost:8000` (ou configurer `VITE_API_URL`)

## Installation

```bash
npm install
```

## Configuration

Copier `.env.example` en `.env` et adapter si besoin :

```env
VITE_API_URL=http://localhost:8000
```

## Lancer en dev

```bash
npm run dev
```

Ouvre [http://localhost:5173](http://localhost:5173).

## Build

```bash
npm run build
npm run preview   # prévisualiser le build
```

## Parcours utilisateur

- **Accueil** (`/`) : présentation, liens Connexion / Inscription
- **Connexion** (`/login`) : email + mot de passe → redirection Candidat ou Recruteur
- **Inscription** (`/register`) : email, mot de passe, rôle (candidat/recruteur), nom optionnel
- **Candidat** (`/candidat/*`) : tableau de bord, profil, mes CVs (upload PDF), recherche d’offres, candidatures, score de matching
- **Recruteur** (`/recruteur/*`) : tableau de bord, créer une offre, mes offres, candidatures par offre, matching IA (meilleurs candidats par offre)

## Design

- Sidebar sombre (#0f172a), zone de contenu claire (#f8fafc)
- Couleur principale : bleu (#2563eb)
- Cartes, formulaires et boutons cohérents avec le design system dans `src/index.css`

## Liaison backend

Tous les appels passent par `src/services/api.js` (baseURL + Bearer JWT). Services utilisés :

- `authService` : register, login, getMe
- `cvService` : uploadCV, getMyCVs, deleteCV
- `matchingService` : getJobOffers, getMatchingScore, applyToOffer, getMyCandidatures
- `offresService` : createOffre, getOffresRecruteur, getCandidaturesForOffre, getMeilleursCandidats
