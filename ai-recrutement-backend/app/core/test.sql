-- Insertion des utilisateurs de test
INSERT INTO utilisateurs (id, email, mot_de_passe, role) VALUES
-- Candidats
('405a982a-1e54-4f10-aadc-cfaa7a43440c', 'debug_test@example.com', '$2b$12$zivZsaCi5fTAQKH08LNOoeQ7/oEmQNCJ/xlLDpV13i3LF87Gt3Irq', 'candidat'),
('95711eba-a109-4976-b818-cd97df833b3c', 'salwa@gmail.com', '$2b$12$WxfooiX5hDJrOAkRfcwQ5enp/WMCiCATasUThMe0adi8We1KKr1je', 'candidat'),
-- Recruteurs
('9018bcce-5ea5-4d7a-9a03-54d9a9a40bdc', 'imane@gmail.com', '$2b$12$dXPhxfO7TKhtnGkiX9JG3.xv7doOIq6InQv.M1kgaTBOcCJyV7/We', 'recruteur'),
('ae3775e1-81a0-4a02-932f-06a5a6114114', 'admin@gmail.com', '$2b$12$7S7tamtHHqKdNewLlMWXfOWorZiBafzfM1TnA6tSS69OZxGPuL5OG', 'recruteur'),
('fb72f340-dea8-48df-9eee-a1af5ce299ff', 'recrutement@capgemini.com', '$2b$12$examplehashcapgemini', 'recruteur')
ON CONFLICT (id) DO NOTHING;

-- Insertion des candidats
INSERT INTO candidats (id, user_id, nom, telephone, localisation, date_naissance) VALUES
('80837b79-19e5-45c8-bb8f-c4642a3b579b', '95711eba-a109-4976-b818-cd97df833b3c', 'salwa', '+33 6 98 76 54 32', 'Paris, France', '1995-08-15'),
('87fa7cba-8914-40c8-a41c-c51620f5da4f', '405a982a-1e54-4f10-aadc-cfaa7a43440c', 'Debug User', '+33 7 12 34 56 78', 'Lyon, France', '1992-03-22')
ON CONFLICT (id) DO NOTHING;

-- Insertion des recruteurs
INSERT INTO recruteurs (id, user_id, entreprise, poste, telephone) VALUES
('3df68aaa-91a4-4328-8218-963d5946abf9', '9018bcce-5ea5-4d7a-9a03-54d9a9a40bdc', 'freelancer', 'Responsable RH', '+33 6 11 22 33 44'),
('f7a69449-a425-445f-8a02-4ebc9604dd67', 'ae3775e1-81a0-4a02-932f-06a5a6114114', 'sparkmind', 'CEO', '+33 6 99 88 77 66'),
('d6a68a63-c48e-4372-b69a-c77657fc5009', 'fb72f340-dea8-48df-9eee-a1af5ce299ff', 'Capgemini', 'Responsable Recrutement', '+33 6 12 34 56 78')
ON CONFLICT (id) DO NOTHING;

-- Insertion des CVs
INSERT INTO cvs (id, candidat_id, fichier_nom, texte_brut, json_structure, embedding) VALUES
-- CV Salwa Ben Mida
(
    gen_random_uuid(),
    '80837b79-19e5-45c8-bb8f-c4642a3b579b',
    'salwa_ben_mida_cv.pdf',
    'Data Analyst avec 3 ans d''expérience en analyse de données et visualisation. Maîtrise de SQL, Python et Tableau.',
    '{
        "personal": {
            "full_name": "Salwa",
            "email": "salwa@gmail.com",
            "phone": "+33 6 98 76 54 32",
            "location": "Paris, France",
            "birth_date": "1995-08-15"
        },
        "summary": "Data Analyst passionnée par la transformation des données en insights actionnables. 3 ans d''expérience dans l''analyse de données clients et la création de dashboards.",
        "experience": [
            {
                "position": "Data Analyst",
                "company": "DataInsights",
                "start_date": "2021-09-01",
                "end_date": null,
                "description": "Analyse de données clients, création de rapports automatisés, développement de dashboards Tableau"
            },
            {
                "position": "Analyste Junior",
                "company": "AnalyticsPro",
                "start_date": "2020-01-15",
                "end_date": "2021-08-31",
                "description": "Support aux équipes marketing, analyse de campagnes, reporting Excel"
            }
        ],
        "skills": [
            {"name": "SQL", "level": "Expert"},
            {"name": "Python", "level": "Avancé"},
            {"name": "Tableau", "level": "Avancé"},
            {"name": "Excel", "level": "Expert"},
            {"name": "Power BI", "level": "Intermédiaire"}
        ],
        "education": [
            {
                "degree": "Master en Statistiques",
                "school": "Université Paris-Dauphine",
                "year": 2019
            }
        ]
    }'::jsonb,
    ARRAY_FILL(0.12, ARRAY[1536])::vector
),
-- CV Debug User
(
    gen_random_uuid(),
    '87fa7cba-8914-40c8-a41c-c51620f5da4f',
    'debug_user_cv.pdf',
    'Développeur Full Stack avec expertise en JavaScript et React. Passionné par le développement web moderne.',
    '{
        "personal": {
            "full_name": "Debug User",
            "email": "debug_test@example.com",
            "phone": "+33 7 12 34 56 78",
            "location": "Lyon, France"
        },
        "summary": "Développeur Full Stack avec 4 ans d''expérience dans le développement d''applications web. Focus sur la qualité du code et les bonnes pratiques.",
        "experience": [
            {
                "position": "Développeur Full Stack",
                "company": "TechDev",
                "start_date": "2020-03-01",
                "end_date": null,
                "description": "Développement frontend avec React, backend avec Node.js, architecture microservices"
            },
            {
                "position": "Développeur Frontend",
                "company": "WebSolutions",
                "start_date": "2018-06-01",
                "end_date": "2020-02-28",
                "description": "Développement d''interfaces utilisateur responsive, intégration avec APIs REST"
            }
        ],
        "skills": [
            {"name": "JavaScript", "level": "Expert"},
            {"name": "React", "level": "Expert"},
            {"name": "Node.js", "level": "Avancé"},
            {"name": "TypeScript", "level": "Avancé"},
            {"name": "Docker", "level": "Intermédiaire"}
        ]
    }'::jsonb,
    ARRAY_FILL(0.25, ARRAY[1536])::vector
);

-- Insertion des expériences
INSERT INTO experiences (id, cv_id, poste, entreprise, date_debut, date_fin, description)
SELECT 
    gen_random_uuid(),
    (SELECT id FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'),
    'Data Analyst',
    'DataInsights',
    '2021-09-01',
    NULL,
    'Analyse de données clients, création de rapports automatisés, développement de dashboards Tableau'
UNION ALL
SELECT 
    gen_random_uuid(),
    (SELECT id FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'),
    'Analyste Junior',
    'AnalyticsPro',
    '2020-01-15',
    '2021-08-31',
    'Support aux équipes marketing, analyse de campagnes, reporting Excel'
UNION ALL
SELECT 
    gen_random_uuid(),
    (SELECT id FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f'),
    'Développeur Full Stack',
    'TechDev',
    '2020-03-01',
    NULL,
    'Développement frontend avec React, backend avec Node.js, architecture microservices'
UNION ALL
SELECT 
    gen_random_uuid(),
    (SELECT id FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f'),
    'Développeur Frontend',
    'WebSolutions',
    '2018-06-01',
    '2020-02-28',
    'Développement d''interfaces utilisateur responsive, intégration avec APIs REST';

-- Insertion des compétences
INSERT INTO competences (id, cv_id, nom, categorie, niveau)
-- Compétences Salwa
SELECT gen_random_uuid(), id, 'SQL', 'Bases de données', 'Expert' FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'
UNION ALL
SELECT gen_random_uuid(), id, 'Python', 'Programmation', 'Avancé' FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'
UNION ALL
SELECT gen_random_uuid(), id, 'Tableau', 'Visualisation', 'Avancé' FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'
UNION ALL
SELECT gen_random_uuid(), id, 'Excel', 'Analyse', 'Expert' FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'
UNION ALL
SELECT gen_random_uuid(), id, 'Power BI', 'Visualisation', 'Intermédiaire' FROM cvs WHERE candidat_id = '80837b79-19e5-45c8-bb8f-c4642a3b579b'
-- Compétences Debug User
UNION ALL
SELECT gen_random_uuid(), id, 'JavaScript', 'Langages', 'Expert' FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f'
UNION ALL
SELECT gen_random_uuid(), id, 'React', 'Frontend', 'Expert' FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f'
UNION ALL
SELECT gen_random_uuid(), id, 'Node.js', 'Backend', 'Avancé' FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f'
UNION ALL
SELECT gen_random_uuid(), id, 'TypeScript', 'Langages', 'Avancé' FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f'
UNION ALL
SELECT gen_random_uuid(), id, 'Docker', 'DevOps', 'Intermédiaire' FROM cvs WHERE candidat_id = '87fa7cba-8914-40c8-a41c-c51620f5da4f';

-- Insertion des offres d'emploi
INSERT INTO offres_emploi (id, recruteur_id, titre, description, localisation, type_contrat, salaire_min, salaire_max, experience_requise, json_structure, embedding, statut) VALUES
-- Offre 1: Data Analyst
(
    gen_random_uuid(),
    'f7a69449-a425-445f-8a02-4ebc9604dd67',
    'Data Analyst Senior - IA & Big Data',
    'Rejoignez notre équipe Data pour développer des solutions d''analyse avancée et contribuer à notre plateforme de recrutement intelligente.',
    'Paris (Hybride)',
    'CDI',
    55000,
    70000,
    3,
    '{
        "requirements": {
            "technical_skills": ["SQL", "Python", "Tableau", "Statistics", "Machine Learning Basics"],
            "minimum_experience": 3,
            "education_level": "Bac+5 en Data Science, Statistiques ou équivalent",
            "soft_skills": ["Analyse critique", "Communication", "Travail en équipe", "Curiosité"],
            "languages": ["Français (courant)", "Anglais (professionnel)"]
        },
        "benefits": [
            "Télétravail flexible (3j/semaine)",
            "Mutuelle santé premium",
            "Tickets restaurant (€9/day)",
            "Budget formation annuel (€1500)",
            "Equipement haut de gamme fourni",
            "Prime de participation"
        ],
        "recruitment_process": [
            "Entretien RH (30min)",
            "Test technique (SQL + Python)",
            "Entretien technique (1h)",
            "Rencontre avec l''équipe (45min)",
            "Offre sous 48h"
        ],
        "remote_policy": "hybrid",
        "start_date": "ASAP"
    }'::jsonb,
    ARRAY_FILL(0.15, ARRAY[1536])::vector,
    'ouverte'
),
-- Offre 2: Développeur Full Stack
(
    gen_random_uuid(),
    'd6a68a63-c48e-4372-b69a-c77657fc5009',
    'Développeur Full Stack JavaScript (React/Node.js)',
    'Intégrez notre équipe digitale pour développer des applications innovantes pour nos clients grands comptes.',
    'Paris, Lyon ou Toulouse (Flexible)',
    'CDI',
    48000,
    62000,
    2,
    '{
        "requirements": {
            "technical_skills": ["React", "Node.js", "JavaScript/TypeScript", "REST APIs", "Git", "Docker"],
            "minimum_experience": 2,
            "education_level": "Bac+3/5 en informatique",
            "soft_skills": ["Autonomie", "Esprit d''équipe", "Adaptabilité", "Relation client"],
            "languages": ["Français (courant)", "Anglais (technique)"]
        },
        "benefits": [
            "Télétravail partiel selon projets",
            "Voiture de fonction ou indemnité",
            "Mutuelle entreprise",
            "13ème mois",
            "Évolutions internationales possibles",
            "Formations certifiantes"
        ],
        "recruitment_process": [
            "Préscreening téléphonique",
            "Test technique en ligne",
            "Entretien technique (1h30)",
            "Entretien avec le manager",
            "Réponse sous 1 semaine"
        ],
        "remote_policy": "flexible",
        "project_duration": "Long terme"
    }'::jsonb,
    ARRAY_FILL(0.28, ARRAY[1536])::vector,
    'ouverte'
),
-- Offre 3: Freelance React
(
    gen_random_uuid(),
    '3df68aaa-91a4-4328-8218-963d5946abf9',
    'Développeur React Senior - Mission Freelance',
    'Mission freelance pour le développement d''une application web de gestion de contenu avec React 18 et TypeScript.',
    '100% Remote',
    'Freelance',
    600,
    850,
    5,
    '{
        "requirements": {
            "technical_skills": ["React 18+", "TypeScript", "Tailwind CSS", "React Query/TanStack", "Vite", "Testing"],
            "minimum_experience": 5,
            "freelance_experience": "Requis",
            "soft_skills": ["Autonomie", "Communication", "Gestion du temps", "Proactivité"]
        },
        "conditions": {
            "duration": "6 mois (renouvelable)",
            "workload": "35h/semaine",
            "rate_range": "€600-850/jour",
            "payment_terms": "Facturation mensuelle",
            "equipment": "À la charge du freelance",
            "availability": "Début février 2026"
        },
        "remote_policy": "full_remote",
        "interview_process": [
            "Échange découverte (30min)",
            "Review de code/portfolio",
            "Entretien technique (1h)",
            "Offre sous 72h"
        ]
    }'::jsonb,
    ARRAY_FILL(0.35, ARRAY[1536])::vector,
    'ouverte'
);

-- Insertion des candidatures
INSERT INTO candidatures (id, candidat_id, offre_id, statut, score_matching, explication, date_candidature)
SELECT 
    gen_random_uuid(),
    '80837b79-19e5-45c8-bb8f-c4642a3b579b',
    (SELECT id FROM offres_emploi WHERE titre = 'Data Analyst Senior - IA & Big Data'),
    'pending',
    92.5,
    'Profil exceptionnellement aligné : compétences techniques parfaitement adaptées (SQL, Python, Tableau), expérience pertinente dans le domaine data, profil académique idéal.',
    NOW() - INTERVAL '2 days'
UNION ALL
SELECT 
    gen_random_uuid(),
    '87fa7cba-8914-40c8-a41c-c51620f5da4f',
    (SELECT id FROM offres_emploi WHERE titre = 'Développeur Full Stack JavaScript (React/Node.js)'),
    'accepted',
    88.0,
    'Très bon match technique (React, Node.js, TypeScript). Expérience solide en développement full stack. Entretien technique réussi.',
    NOW() - INTERVAL '5 days'
UNION ALL
SELECT 
    gen_random_uuid(),
    '87fa7cba-8914-40c8-a41c-c51620f5da4f',
    (SELECT id FROM offres_emploi WHERE titre = 'Développeur React Senior - Mission Freelance'),
    'pending',
    76.3,
    'Compétences React/TypeScript excellentes, mais manque d''expérience spécifique en freelance.',
    NOW() - INTERVAL '1 day';

-- Insertion des notifications
INSERT INTO notifications (id, utilisateur_id, titre, message, is_read, type, date_creation)
SELECT 
    gen_random_uuid(),
    u.id,
    'Bienvenue sur AI Recruitment!',
    'Votre compte a été activé avec succès. Commencez à explorer les offres correspondant à votre profil.',
    true,
    'welcome',
    NOW() - INTERVAL '3 days'
FROM utilisateurs u
UNION ALL
SELECT 
    gen_random_uuid(),
    (SELECT id FROM utilisateurs WHERE email = 'salwa@gmail.com'),
    'Votre candidature a été envoyée',
    'Votre candidature pour "Data Analyst Senior - IA & Big Data" a été transmise au recruteur. Score de matching: 92.5%.',
    false,
    'application_submitted',
    NOW() - INTERVAL '1 day'
UNION ALL
SELECT 
    gen_random_uuid(),
    (SELECT id FROM utilisateurs WHERE email = 'debug_test@example.com'),
    'Candidature acceptée! 🎉',
    'Félicitations! Votre candidature pour "Développeur Full Stack JavaScript" a été acceptée. Le recruteur vous contactera pour la suite.',
    false,
    'application_accepted',
    NOW() - INTERVAL '2 days'
UNION ALL
SELECT 
    gen_random_uuid(),
    (SELECT id FROM utilisateurs WHERE email = 'admin@gmail.com'),
    'Nouvelle candidature à fort potentiel',
    'Salwa Ben Mida a postulé à votre offre "Data Analyst Senior". Score IA: 92.5% - Profil très prometteur!',
    false,
    'new_application',
    NOW() - INTERVAL '6 hours';
