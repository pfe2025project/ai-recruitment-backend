-- 1. Remove old score columns from candidate_profiles
ALTER TABLE candidate_profiles
    DROP COLUMN IF EXISTS skills_score,
    DROP COLUMN IF EXISTS score_contexte,
    DROP COLUMN IF EXISTS extracted_skills;


-- 2. Add global_score and skill_score to applications table
ALTER TABLE applications
    ADD COLUMN IF NOT EXISTS global_score NUMERIC,
    ADD COLUMN IF NOT EXISTS skill_score NUMERIC;

-- 3. Add column for full CV text
ALTER TABLE candidate_profiles
    ADD COLUMN IF NOT EXISTS cv TEXT;

-- 4. Replace old skills column with three new skill columns
-- Step 1: Drop old skills column
ALTER TABLE candidate_profiles
    DROP COLUMN IF EXISTS skills;

-- Step 2: Add new skill columns
ALTER TABLE candidate_profiles
    ADD COLUMN IF NOT EXISTS skillner_skills TEXT[],
    ADD COLUMN IF NOT EXISTS py_skills TEXT[],
    ADD COLUMN IF NOT EXISTS added_skills TEXT[];
