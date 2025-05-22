-- =====================================================
-- MIGRATION HIREMATCH AI - SYSTÈME MULTI-RÔLES
-- =====================================================
-- ⚠️ ATTENTION : Ce script supprime les anciennes tables
-- Assurez-vous d'avoir une sauvegarde avant d'exécuter !

-- =====================================================
-- 1. SUPPRESSION DES ANCIENNES TABLES
-- =====================================================

-- Supprimer les tables dans l'ordre inverse des dépendances
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS candidate_profiles CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS recruiters CASCADE;

-- =====================================================
-- 2. CRÉATION DES NOUVELLES TABLES
-- =====================================================

-- Table principale des utilisateurs (unifiée)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users (id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des rôles utilisateur (relation many-to-many)
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('candidate', 'recruiter')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, role)
);

-- Index pour améliorer les performances
CREATE INDEX idx_user_roles_user_id ON user_roles (user_id);
CREATE INDEX idx_user_roles_role ON user_roles (role);
CREATE INDEX idx_user_roles_active ON user_roles (user_id, role, is_active);

-- =====================================================
-- 3. TABLES SPÉCIALISÉES PAR RÔLE
-- =====================================================

-- Profils candidats (données spécifiques aux candidats)
CREATE TABLE candidate_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    experience JSONB,              -- JSON pour flexibilité
    education JSONB,               -- JSON pour flexibilité
    skills TEXT[],                 -- Array de compétences
    cv_url TEXT,                   -- URL du CV stocké
    cv_filename TEXT,              -- Nom original du fichier
    location TEXT,                 -- Localisation préférée
    salary_expectation JSONB,      -- {min: 50000, max: 70000, currency: "EUR"}
    availability_date DATE,        -- Date de disponibilité
    job_preferences JSONB,         -- Préférences de travail (remote, on-site, etc.)
    linkedin_url TEXT,
    portfolio_url TEXT,
    github_url TEXT,
    skills_score NUMERIC DEFAULT 0,     -- Score calculé par IA
    context_score NUMERIC DEFAULT 0,    -- Score contextuel
    is_actively_looking BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)  -- Un seul profil candidat par utilisateur
);

-- Profils recruteurs (données spécifiques aux recruteurs)
CREATE TABLE recruiter_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    position TEXT,                 -- Poste du recruteur
    department TEXT,               -- Département
    hire_authority BOOLEAN DEFAULT false,  -- Peut prendre des décisions d'embauche
    specializations TEXT[],        -- Domaines de spécialisation
    linkedin_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)  -- Un seul profil recruteur par utilisateur
);

-- =====================================================
-- 4. TABLES MÉTIER
-- =====================================================

-- Entreprises (liées aux recruteurs)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    website TEXT,
    email TEXT,
    phone TEXT,
    logo_url TEXT,
    description TEXT,
    industry TEXT,                 -- Secteur d'activité
    size_category TEXT CHECK (size_category IN ('startup', 'small', 'medium', 'large', 'enterprise')),
    location TEXT,                 -- Siège social
    founded_year INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Relation recruteurs-entreprises (many-to-many car un recruteur peut travailler pour plusieurs entreprises)
CREATE TABLE company_recruiters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    role_in_company TEXT DEFAULT 'recruiter',  -- 'recruiter', 'hiring_manager', 'hr_director'
    is_primary BOOLEAN DEFAULT false,          -- Recruteur principal pour cette entreprise
    can_post_jobs BOOLEAN DEFAULT true,
    can_manage_applications BOOLEAN DEFAULT true,
    joined_company_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, user_id)
);

-- Offres d'emploi
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies (id) ON DELETE CASCADE,
    created_by_user_id UUID NOT NULL REFERENCES users (id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT[],           -- Compétences requises
    nice_to_have TEXT[],          -- Compétences souhaitées
    location TEXT,
    remote_policy TEXT CHECK (remote_policy IN ('on-site', 'remote', 'hybrid', 'flexible')),
    employment_type TEXT CHECK (employment_type IN ('full-time', 'part-time', 'contract', 'internship', 'freelance')),
    experience_level TEXT CHECK (experience_level IN ('entry', 'junior', 'mid', 'senior', 'lead', 'executive')),
    education_level TEXT CHECK (education_level IN ('high-school', 'bachelor', 'master', 'phd', 'certification')),
    salary_range JSONB,           -- {min: 50000, max: 70000, currency: "EUR", period: "yearly"}
    benefits TEXT[],              -- Avantages
    application_deadline DATE,
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'closed', 'archived')),
    view_count INTEGER DEFAULT 0,
    application_count INTEGER DEFAULT 0,
    file_url TEXT,                -- Document job description complet
    ai_extracted_skills TEXT[],   -- Compétences extraites par IA
    ai_matching_keywords TEXT[],  -- Mots-clés pour matching
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les recherches
CREATE INDEX idx_jobs_status ON jobs (status);
CREATE INDEX idx_jobs_location ON jobs (location);
CREATE INDEX idx_jobs_company ON jobs (company_id);
CREATE INDEX idx_jobs_created_by ON jobs (created_by_user_id);
CREATE INDEX idx_jobs_employment_type ON jobs (employment_type);
CREATE INDEX idx_jobs_experience_level ON jobs (experience_level);

-- =====================================================
-- 5. SYSTÈME DE CANDIDATURES
-- =====================================================

-- Candidatures
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
    candidate_user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'shortlisted', 'interview_scheduled', 'interviewed', 'offered', 'hired', 'rejected', 'withdrawn')),
    cover_letter TEXT,
    custom_cv_url TEXT,           -- CV spécifique pour cette candidature
    ai_matching_score NUMERIC,    -- Score de matching IA (0-100)
    ai_skills_match JSONB,        -- Détail du matching des compétences
    recruiter_notes TEXT,         -- Notes du recruteur
    candidate_notes TEXT,         -- Notes privées du candidat
    applied_at TIMESTAMP DEFAULT NOW(),
    last_status_change TIMESTAMP DEFAULT NOW(),
    interview_scheduled_at TIMESTAMP,
    offer_details JSONB,          -- Détails de l'offre si applicable
    UNIQUE(job_id, candidate_user_id)  -- Un candidat ne peut postuler qu'une fois par job
);

-- Historique des changements de statut
CREATE TABLE application_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    changed_by_user_id UUID REFERENCES users (id) ON DELETE SET NULL,
    notes TEXT,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- 6. SYSTÈME DE NOTIFICATIONS
-- =====================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('application_status', 'new_job_match', 'profile_view', 'message', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB,                   -- Données supplémentaires (IDs, liens, etc.)
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_unread ON notifications (user_id, is_read);

-- =====================================================
-- 7. TRIGGERS POUR MISE À JOUR AUTOMATIQUE
-- =====================================================

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_candidate_profiles_updated_at 
    BEFORE UPDATE ON candidate_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recruiter_profiles_updated_at 
    BEFORE UPDATE ON recruiter_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour l'historique des candidatures
CREATE OR REPLACE FUNCTION track_application_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO application_status_history (application_id, previous_status, new_status, changed_at)
        VALUES (NEW.id, OLD.status, NEW.status, NOW());
        NEW.last_status_change = NOW();
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER track_application_status_trigger
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION track_application_status_change();

-- =====================================================
-- 8. DONNÉES DE TEST (OPTIONNEL)
-- =====================================================

-- Vous pouvez décommenter cette section pour avoir des données de test

/*
-- Insertion d'un utilisateur test (vous devrez d'abord vous inscrire via l'app)
-- INSERT INTO users (id, email, full_name) VALUES 
-- ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'Test User');

-- INSERT INTO user_roles (user_id, role) VALUES 
-- ('550e8400-e29b-41d4-a716-446655440000', 'candidate'),
-- ('550e8400-e29b-41d4-a716-446655440000', 'recruiter');
*/

-- =====================================================
-- 9. VUES UTILES (OPTIONNEL)
-- =====================================================

-- Vue pour les utilisateurs avec leurs rôles
CREATE VIEW users_with_roles AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.avatar_url,
    u.phone,
    u.created_at,
    ARRAY_AGG(ur.role ORDER BY ur.role) as roles,
    COUNT(ur.role) as role_count
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_active = true
GROUP BY u.id, u.email, u.full_name, u.avatar_url, u.phone, u.created_at;

-- Vue pour les jobs avec informations de l'entreprise
CREATE VIEW jobs_with_company AS
SELECT 
    j.*,
    c.name as company_name,
    c.logo_url as company_logo,
    c.location as company_location,
    c.website as company_website
FROM jobs j
JOIN companies c ON j.company_id = c.id;

-- =====================================================
-- 10. PERMISSIONS RLS (ROW LEVEL SECURITY) - OPTIONNEL
-- =====================================================

-- Activer RLS sur les tables sensibles
-- ALTER TABLE candidate_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE recruiter_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Exemple de politique RLS
-- CREATE POLICY "Users can only see their own candidate profile" ON candidate_profiles
--     FOR ALL USING (auth.uid() = user_id);

-- =====================================================
-- MIGRATION TERMINÉE ✅
-- =====================================================

-- Pour vérifier que tout s'est bien passé :
SELECT 'Migration completed successfully!' as status;

-- Vérifier les tables créées :
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;