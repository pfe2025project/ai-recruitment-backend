# AI Matching Service Explanation

This document explains the workings of the AI Matching Service within the `ai-recruitment-backend` project. It is designed to help frontend developers understand how to integrate with this service.

## 1. Purpose

The AI Matching Service is responsible for calculating the compatibility (match score) between candidates and jobs. It uses a hybrid AI approach, combining multiple models to provide comprehensive and accurate matching results. The service also supports skill extraction and similarity calculations between arbitrary texts.

## 2. Core Components

The primary logic for the matching service resides in the following files:

*   <mcfile name="matching_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\matching_service.py"></mcfile>: Contains the main business logic for matching candidates to jobs and vice-versa, and orchestrates the use of AI models.
*   <mcfile name="hybrid_ai_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\hybrid_ai_service.py"></mcfile>: (Placeholder) This file is intended to house the actual AI model implementations and their logic for calculating scores and extracting skills.
*   <mcfile name="ai_matching_routes.py" path="c:\Users\MSI\ai-recruitment-backend\app\routes\ai_matching_routes.py"></mcfile>: Defines the API endpoints through which the matching service can be accessed.

## 3. How the Matching Works

The matching process involves several steps:

1.  **Data Retrieval**: The service fetches relevant data for candidates (CVs, skills, experience, education) and jobs (title, description, requirements, location) from the database.
2.  **Text Preparation**: The retrieved structured and unstructured data for both candidates and jobs is combined and processed into a textual format suitable for AI model input.
3.  **Hybrid AI Scoring**: The prepared texts are fed into the `HybridAIService`. This service is designed to utilize multiple AI models (e.g., SBERT for semantic similarity, Skill2Vec for skill-based similarity) to generate different scores.
4.  **Score Aggregation**: The individual scores from different AI models are combined to produce a final `hybrid_score`. The service also provides the individual model scores (e.g., `sbert_similarity`, `skill2vec_similarity`).
5.  **Skill Matching**: The service identifies and returns common skills between the candidate's resume and the job's requirements.
6.  **Result Structuring**: The calculated scores and other relevant job/candidate details are structured into a comprehensive response, sorted by the hybrid match score.

**Note on Database Persistence**: Currently, the calculated match scores (including individual model scores and the hybrid score) are **returned as part of the API response** but are **now automatically saved to a dedicated database table (`candidate_job_matches`)** by the service itself.

## 4. Automatic Matching Triggers

*   **CV Upload**: When a candidate's CV is fully uploaded and its information extracted via the `POST /api/cv` endpoint, the system automatically triggers a candidate-to-job matching process. The results are saved to the `candidate_job_matches` table.
*   **Job Addition**: When a new job offer is added via the `POST /api/jobs` endpoint, the system automatically triggers a job-to-candidate matching process. The results are saved to the `candidate_job_matches` table.

## 5. AI Models Involved (Conceptual)

The `hybrid_ai_service.py` is designed to integrate various AI models. Conceptually, it might include:

*   **SBERT (Sentence-BERT)**: For calculating semantic similarity between the overall candidate text and job description. This model understands the meaning and context of sentences.
*   **Skill2Vec**: For embedding skills into vector space and calculating similarity based on skill sets. This helps in identifying how well a candidate's skills align with job requirements.
*   **SkillNER (Skill Named Entity Recognition)**: For extracting skills from unstructured text (e.g., CVs, job descriptions).

## 6. API Endpoints

The AI Matching Service exposes the following REST API endpoints, defined in <mcfile name="ai_matching_routes.py" path="c:\Users\MSI\ai-recruitment-backend\app\routes\ai_matching_routes.py"></mcfile>:

### 6.1. Match Candidate to Jobs

*   **Endpoint**: `GET /api/ai-matching/candidate/jobs`
*   **Description**: Matches an authenticated candidate to available jobs based on their profile and CV.
*   **Query Parameters**:
    *   `job_ids` (optional): Comma-separated list of specific job UUIDs to match against. If not provided, matches against a broader set of jobs.
    *   `limit` (optional): Maximum number of job matches to return (default: 10).
*   **Authentication**: Requires candidate authentication (JWT token).
*   **Response**: A JSON array of job objects, each including:
    *   `job_id`
    *   `job_title`
    *   `job_description`
    *   `job_location`
    *   `job_requirements`
    *   `company_name`
    *   `company_logo`
    *   `match_score` (hybrid score)
    *   `sbert_similarity`
    *   `skill2vec_similarity`
    *   `matched_skills` (skills common to both candidate and job)
    *   `candidate_skills` (skills extracted from candidate's profile)
    *   `job_skills` (skills extracted from job description)
    *   `prediction` (hybrid prediction)
    *   `match_percentage`

### 6.2. Match Job to Candidates

*   **Endpoint**: `GET /api/ai-matching/job/<job_id>/candidates`
*   **Description**: Matches a specific job to available candidates.
*   **Path Parameters**:
    *   `job_id` (required): The UUID of the job to match candidates against.
*   **Query Parameters**:
    *   `candidate_ids` (optional): Comma-separated list of specific candidate UUIDs to match against. If not provided, matches against a broader set of candidates.
    *   `limit` (optional): Maximum number of candidate matches to return (default: 10).
*   **Authentication**: Requires recruiter authentication (JWT token).
*   **Response**: A JSON object containing:
    *   `matches`: A JSON array of candidate objects, each with similar score details as the candidate-to-job matching.
    *   `total_matches`
    *   `job_id`

### 6.3. Get Skill Recommendations

*   **Endpoint**: `GET /api/ai-matching/candidate/skill-recommendations/<job_id>`
*   **Description**: Provides skill recommendations for an authenticated candidate based on a target job, potentially highlighting skill gaps.
*   **Path Parameters**:
    *   `job_id` (required): The UUID of the target job.
*   **Authentication**: Requires candidate authentication.
*   **Response**: JSON object with skill gap analysis and recommendations.

### 6.4. Extract Skills from Text

*   **Endpoint**: `POST /api/ai-matching/candidate/skills/extract`
*   **Description**: Extracts skills from a provided text string.
*   **Request Body**:
    ```json
    {
        "text": "Your text here, e.g., a resume snippet or job description."
    }
    ```
*   **Authentication**: Requires authentication.
*   **Response**: JSON object containing:
    *   `extracted_skills`: A list of extracted skills.
    *   `skills_count`
    *   `text_length`

### 6.5. Calculate Similarity Between Texts

*   **Endpoint**: `POST /api/ai-matching/similarity/calculate`
*   **Description**: Calculates the hybrid similarity score between two arbitrary text inputs.
*   **Request Body**:
    ```json
    {
        "text1": "First text (e.g., resume content)",
        "text2": "Second text (e.g., job description content)"
    }
    ```
*   **Authentication**: Requires authentication.
*   **Response**: JSON object containing:
    *   `hybrid_score`
    *   `sbert_similarity`
    *   `skill2vec_similarity`
    *   `resume_skills` (skills extracted from text1)
    *   `job_skills` (skills extracted from text2)
    *   `hybrid_prediction`

### 6.6. Health Check

*   **Endpoint**: `GET /api/ai-matching/health`
*   **Description**: Provides a health check for the AI matching service and its underlying models.
*   **Authentication**: None required.
*   **Response**: JSON object indicating the status of the service and models.

### 6.7. Add New Job

*   **Endpoint**: `POST /api/jobs`
*   **Description**: Adds a new job offer and automatically triggers job-to-candidate matching.
*   **Request Body**: JSON object containing job details (e.g., `title`, `description`, `requirements`, `location`, `company_id`, etc.).
*   **Authentication**: Requires authentication.
*   **Response**: Success message with the new job's ID or an error.

## 7. Integration Notes for Frontend

*   **Base URL**: All API endpoints are prefixed with `/api/ai-matching`.
*   **CORS Configuration**: Cross-Origin Resource Sharing (CORS) has been enabled for the Flask application to allow requests from different origins. This ensures that frontend applications hosted on different domains can interact with the backend API without issues.
*   **Authentication**: Most endpoints require a JWT token in the `Authorization` header (e.g., `Bearer <token>`). Ensure your frontend handles token acquisition and attachment.
*   **Error Handling**: The API returns standard HTTP status codes (e.g., 200 for success, 400 for bad request, 401 for unauthorized, 500 for internal server error) and JSON error messages.
*   **Data Formats**: Expect JSON for both request bodies (where applicable) and responses.
*   **Testing**: You can use tools like Postman, Insomnia, or `curl` to test these endpoints directly against the running backend.
*   **Triggering Matching**: Note that matching is now automatically triggered upon CV upload and job creation, so no separate API calls are needed from the frontend for this purpose.

This document should provide a clear overview for integrating with the AI Matching Service. For detailed request/response schemas, refer to the specific endpoint definitions in <mcfile name="ai_matching_routes.py" path="c:\Users\MSI\ai-recruitment-backend\app\routes\ai_matching_routes.py"></mcfile>, <mcfile name="job.py" path="c:\Users\MSI\ai-recruitment-backend\app\routes\job.py"></mcfile> and the service logic in <mcfile name="matching_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\matching_service.py"></mcfile>, <mcfile name="cv_service.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\cv_service.py"></mcfile>, <mcfile name="job_services.py" path="c:\Users\MSI\ai-recruitment-backend\app\services\job_services.py"></mcfile>.