CREATE TABLE IF NOT EXISTS candidate_job_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES public.candidates(id) ON DELETE CASCADE,
    job_id UUID REFERENCES public.jobs(id) ON DELETE CASCADE,
    match_score NUMERIC(5, 2) NOT NULL,
    sbert_similarity NUMERIC(5, 2),
    skill2vec_similarity NUMERIC(5, 2),
    matched_skills JSONB,
    candidate_skills JSONB,
    job_skills JSONB,
    prediction TEXT,
    match_percentage NUMERIC(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.candidate_job_matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Candidates can view their own job matches" ON public.candidate_job_matches
FOR SELECT TO authenticated USING (candidate_id = auth.uid());

CREATE POLICY "Candidates can insert their own job matches" ON public.candidate_job_matches
FOR INSERT TO authenticated WITH CHECK (candidate_id = auth.uid());

CREATE POLICY "Candidates can update their own job matches" ON public.candidate_job_matches
FOR UPDATE TO authenticated USING (candidate_id = auth.uid());

CREATE POLICY "Candidates can delete their own job matches" ON public.candidate_job_matches
FOR DELETE TO authenticated USING (candidate_id = auth.uid());

-- Optional: Policy for recruiters to view matches for jobs they own
-- Assuming 'jobs' table has a 'recruiter_id' column
-- CREATE POLICY "Recruiters can view matches for their jobs" ON public.candidate_job_matches
-- FOR SELECT TO authenticated USING (job_id IN (SELECT id FROM public.jobs WHERE recruiter_id = auth.uid()));

-- Optional: Policy for anon role to insert/update if authenticated (for RLS on storage)
-- This is a more permissive policy, use with caution
CREATE POLICY "Allow anon insert if authenticated" ON public.candidate_job_matches
FOR INSERT TO anon WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow anon update if authenticated" ON public.candidate_job_matches
FOR UPDATE TO anon USING (auth.role() = 'authenticated');