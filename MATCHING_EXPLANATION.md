# AI Matching Service Explanation

This document explains how the AI matching service calculates and stores matches between candidates and jobs, and how these matches can be fetched for frontend display.

## 1. Matching Logic (`hybrid_ai_service.py`)

The core matching logic resides in the <mcfile name="hybrid_ai_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\hybrid_ai_service.py"></mcfile> file, specifically within the <mcsymbol name="calculate_hybrid_score" filename="hybrid_ai_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\hybrid_ai_service.py" startline="18" type="function"></mcsymbol> function. This function takes two text inputs: `text1` (resume content) and `text2` (job description content).

Here's a breakdown of the process:

- **Skill Extraction**: The `extract_skills_dict` method is used to identify and extract relevant skills from both the resume and job description.
- **SBERT Encoding**: The original text inputs (`text1` and `text2`) are combined with their respective extracted skills. This combined text is then encoded into numerical embeddings using a Sentence-BERT model (`all-MiniLM-L6-v2`). This allows the model to capture the semantic meaning of the text, including the influence of specific skills.
- **Semantic Similarity**: The cosine similarity between the SBERT embeddings of the resume and job description is calculated. This represents the semantic similarity between the two.
- **Skill-Based Similarity**: The number of common skills between the resume and job description is determined, and a skill similarity score is calculated based on the proportion of common skills relative to the total job skills.
- **Hybrid Score Calculation**: A final `hybrid_score` is calculated by combining the `semantic_similarity` and `skill_similarity` using predefined weights (currently 0.8 for semantic and 0.2 for skill-based). This allows for a balanced assessment that considers both the overall meaning and specific skill alignment.
- **Prediction**: Based on the `hybrid_score`, a `hybrid_prediction` (e.g., "match" or "no_match") is made.

## 2. Match Generation and Storage (`matching_service.py`)

The <mcfile name="matching_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\matching_service.py"></mcfile> file is responsible for orchestrating the matching process and storing the results. It contains functions like `match_candidate_to_jobs` and `match_job_to_candidates`.

- **Text Preparation**: Within these functions, `candidate_text` (which becomes `text1`) is constructed from various candidate profile fields (e.g., `cv_path`, `skillner_skills`, `experience`, `education`). Similarly, `job_text` (which becomes `text2`) is constructed from job fields (e.g., `title`, `description`, `location`, `requirements`).
- **Invoking Hybrid AI Service**: The prepared `candidate_text` and `job_text` are then passed to the <mcsymbol name="calculate_hybrid_score" filename="hybrid_ai_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\hybrid_ai_service.py" startline="18" type="function"></mcsymbol> function in <mcfile name="hybrid_ai_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\hybrid_ai_service.py"></mcfile>.
- **Storing Matches**: The results from `calculate_hybrid_score` (including `hybrid_score`, `semantic_score`, `skill_similarity`, `resume_skills`, `job_skills`, and `hybrid_prediction`) are then stored in the database. The specific table for storing these matches is likely `candidate_job_matches` as indicated by the `db/add_candidate_job_matches_table.sql` file.

### Database Schema for Matches

The `candidate_job_matches` table (defined in <mcfile name="add_candidate_job_matches_table.sql" path="c:\Users\MSI\ai-recruitment-backend\db\add_candidate_job_matches_table.sql"></mcfile>) would typically store:

- `id`: Unique identifier for the match.
- `candidate_id`: Foreign key referencing the candidate.
- `job_id`: Foreign key referencing the job.
- `hybrid_score`: The calculated hybrid score.
- `semantic_score`: The semantic similarity score.
- `skill_similarity`: The skill-based similarity score.
- `hybrid_prediction`: The match prediction (e.g., 'match', 'no_match').
- `matched_at`: Timestamp of when the match was made.
- `resume_skills`: Array of skills extracted from the resume.
- `job_skills`: Array of skills extracted from the job description.

## 3. Fetching Matches in the Frontend

To fetch these matches in the frontend, you would typically interact with an API endpoint exposed by the backend. Based on the file structure, the <mcfile name="ai_matching_routes.py" path="c:\Users\MSI\ai-recruitment-backend\app\routes\ai_matching_routes.py"></mcfile> file likely defines the API routes for AI matching.

Assuming a RESTful API, you would make HTTP requests to retrieve match data. For example:

Assuming a RESTful API, you would make HTTP requests to retrieve match data. The <mcfile name="ai_matching_routes.py" path="c:\Users\MSI\ai-recruitment-backend\app\routes\ai_matching_routes.py"></mcfile> file defines the following relevant API endpoints:

- **For a candidate to get their job matches**: `GET /api/ai-matching/candidate/jobs`
  - This endpoint returns a list of jobs matched to the authenticated candidate.
- **For a recruiter to get candidate matches for a specific job**: `GET /api/ai-matching/job/<job_id>/candidates`
  - This endpoint returns a list of candidates matched to the specified job ID.

These endpoints query the `candidate_job_matches` table, filter by the relevant `candidate_id` or `job_id`, and return the match data, typically ordered by `hybrid_score`.

### Example Frontend Fetch (Conceptual JavaScript)

```javascript
// Example: Fetch job matches for the authenticated candidate
async function fetchCandidateJobMatches() {
    try {
        // Assuming authentication is handled (e.g., via JWT in headers)
        const response = await fetch('/api/ai-matching/candidate/jobs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const matches = await response.json();
        console.log('Candidate Job Matches:', matches);
        // Render matches in your UI
    } catch (error) {
        console.error('Error fetching candidate job matches:', error);
    }
}

// Example: Fetch candidate matches for a specific job ID
async function fetchJobCandidateMatches(jobId) {
    try {
        const response = await fetch(`/api/ai-matching/job/${jobId}/candidates`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const matches = await response.json();
        console.log('Job Candidate Matches:', matches);
        // Render matches in your UI
    } catch (error) {
        console.error('Error fetching job candidate matches:', error);
    }
}

// Call the functions with actual IDs or when appropriate
// fetchCandidateJobMatches();
// fetchJobCandidateMatches('your-job-uuid-here');
```

This conceptual example demonstrates how a frontend application would interact with the backend API to retrieve the stored matching results, which can then be displayed to the user.

This conceptual example demonstrates how a frontend application would interact with the backend API to retrieve the stored matching results, which can then be displayed to the user.