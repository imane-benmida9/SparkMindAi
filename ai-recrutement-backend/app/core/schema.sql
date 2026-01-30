
CREATE TYPE role_enum AS ENUM ('candidat', 'recruteur');
CREATE TYPE statut_offre_enum AS ENUM ('ouverte', 'fermee');
CREATE TYPE statut_candidature_enum AS ENUM ('pending', 'accepted', 'rejected');


CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role role_enum NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    date_creation TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_utilisateurs_email ON utilisateurs(email);
CREATE INDEX idx_utilisateurs_role ON utilisateurs(role);


CREATE TABLE candidats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    localisation VARCHAR(255),
    date_naissance DATE
);

CREATE INDEX idx_candidats_user_id ON candidats(user_id);
CREATE INDEX idx_candidats_localisation ON candidats(localisation);


CREATE TABLE recruteurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    entreprise VARCHAR(255) NOT NULL,
    poste VARCHAR(255),
    telephone VARCHAR(20)
);

CREATE INDEX idx_recruteurs_user_id ON recruteurs(user_id);
CREATE INDEX idx_recruteurs_entreprise ON recruteurs(entreprise);


CREATE TABLE cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidat_id UUID NOT NULL REFERENCES candidats(id) ON DELETE CASCADE,
    fichier_nom VARCHAR(255) NOT NULL,
    texte_brut TEXT,
    json_structure JSONB,
    date_upload TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_cvs_candidat_id ON cvs(candidat_id);
CREATE INDEX idx_cvs_date_upload ON cvs(date_upload DESC);
CREATE INDEX idx_cvs_json_structure ON cvs USING GIN (json_structure);


CREATE TABLE experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL REFERENCES cvs(id) ON DELETE CASCADE,
    poste VARCHAR(255) NOT NULL,
    entreprise VARCHAR(255),
    date_debut DATE,
    date_fin DATE,
    description TEXT,
    CONSTRAINT chk_dates_experience 
        CHECK (date_fin IS NULL OR date_fin >= date_debut)
);

CREATE INDEX idx_experiences_cv_id ON experiences(cv_id);
CREATE INDEX idx_experiences_poste ON experiences(poste);
CREATE INDEX idx_experiences_entreprise ON experiences(entreprise);


CREATE TABLE competences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL REFERENCES cvs(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    categorie VARCHAR(100),
    niveau VARCHAR(50)
);

CREATE INDEX idx_competences_cv_id ON competences(cv_id);
CREATE INDEX idx_competences_nom ON competences(nom);
CREATE INDEX idx_competences_categorie ON competences(categorie);


CREATE TABLE offres_emploi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recruteur_id UUID NOT NULL REFERENCES recruteurs(id) ON DELETE CASCADE,
    titre VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    localisation VARCHAR(255),
    type_contrat VARCHAR(50),
    salaire_min DECIMAL(10,2),
    salaire_max DECIMAL(10,2),
    experience_requise INTEGER,
    date_publication TIMESTAMP DEFAULT NOW() NOT NULL,
    statut statut_offre_enum DEFAULT 'ouverte' NOT NULL,
    CONSTRAINT chk_salaire 
        CHECK (salaire_max IS NULL OR salaire_max >= salaire_min)
);

CREATE INDEX idx_offres_recruteur_id ON offres_emploi(recruteur_id);
CREATE INDEX idx_offres_localisation ON offres_emploi(localisation);
CREATE INDEX idx_offres_statut ON offres_emploi(statut);
CREATE INDEX idx_offres_date_publication ON offres_emploi(date_publication DESC);


CREATE TABLE candidatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidat_id UUID NOT NULL REFERENCES candidats(id) ON DELETE CASCADE,
    offre_id UUID NOT NULL REFERENCES offres_emploi(id) ON DELETE CASCADE,
    statut statut_candidature_enum DEFAULT 'pending' NOT NULL,
    score_matching DECIMAL(5,2),
    explication TEXT,
    date_candidature TIMESTAMP DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_score 
        CHECK (score_matching IS NULL OR (score_matching >= 0 AND score_matching <= 100)),
    CONSTRAINT uq_candidat_offre 
        UNIQUE (candidat_id, offre_id)
);

CREATE INDEX idx_candidatures_candidat_id ON candidatures(candidat_id);
CREATE INDEX idx_candidatures_offre_id ON candidatures(offre_id);
CREATE INDEX idx_candidatures_score_matching ON candidatures(score_matching DESC);
CREATE INDEX idx_candidatures_statut ON candidatures(statut);


CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    titre VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    type VARCHAR(50),
    date_creation TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_notifications_user_id ON notifications(utilisateur_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_date ON notifications(date_creation DESC);


CREATE OR REPLACE FUNCTION validate_email()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RAISE EXCEPTION 'Email invalide: %', NEW.email;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_email
BEFORE INSERT OR UPDATE ON utilisateurs
FOR EACH ROW
EXECUTE FUNCTION validate_email();
-- Ajouter json_structure à cvs (si pas déjà fait)
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Ajouter json_structure et embedding à offres_emploi
ALTER TABLE offres_emploi 
ADD COLUMN IF NOT EXISTS json_structure JSONB,
ADD COLUMN IF NOT EXISTS embedding vector(1536);