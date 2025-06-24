# New AI Matching API Endpoint

This document describes a new API endpoint added to the AI Matching service. This endpoint allows for the retrieval of detailed match scores (Hybrid, SBERT, and Skill2Vec) for a specific candidate-job pair.

## Endpoint Details

*   **Method**: `GET`
*   **URL**: `/api/ai-matching/candidate/<candidate_id>/job/<job_id>/score`
*   **Description**: Retrieves the hybrid AI match score, SBERT similarity, and Skill2Vec similarity for a given candidate and job.

## Path Parameters

*   `candidate_id` (UUID): The unique identifier of the candidate.
*   `job_id` (UUID): The unique identifier of the job.

## Example Request

```
GET /api/ai-matching/candidate/a1b2c3d4-e5f6-7890-1234-567890abcdef/job/f0e9d8c7-b6a5-4321-fedc-ba9876543210/score
```

## Example Response (200 OK)

```json
{
    "job_id": "f0e9d8c7-b6a5-4321-fedc-ba9876543210",
    "job_title": "Software Engineer",
    "job_description": "Develop and maintain web applications.",
    "job_location": "New York, NY",
    "job_requirements": [
        "Python",
        "Flask",
        "SQL"
    ],
    "company_name": "Tech Solutions Inc.",
    "company_logo": "http://example.com/logo.png",
    "match_score": 0.85,
    "sbert_similarity": 0.92,
    "skill2vec_similarity": 0.78,
    "matched_skills": [
        "Python",
        "SQL"
    ],
    "candidate_skills": [
        "Python",
        "SQL",
        "JavaScript"
    ],
    "job_skills": [
        "Python",
        "Flask",
        "SQL",
        "AWS"
    ],
    "prediction": "High Match",
    "match_percentage": 85.00
}
```

## Error Responses

*   **404 Not Found**: If the `candidate_id` or `job_id` provided does not exist.
    ```json
    {
        "message": "Candidate-job match score not found or invalid IDs."
    }
    ```
*   **500 Internal Server Error**: For any unexpected server-side errors.
    ```json
    {
        "message": "Internal server error",
        "error": "<error_details>"
    }
    ```

## Implementation Details (Backend)

*   **Service Layer**: The `get_candidate_job_match_score` function in `app/services/matching_service.py` is responsible for fetching candidate and job data, constructing text representations, calculating hybrid scores using `HybridAIService`, and compiling the response.
*   **Route Definition**: The endpoint is defined in `app/routes/ai_matching_routes.py` under the `ai_matching_bp` blueprint.