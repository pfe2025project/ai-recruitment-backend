from supabase.client import Client
from flask import current_app
from typing import List, Dict, Optional, Union
import json

def get_jobs_data(filters: Dict[str, Union[str, List[str], int, float]]) -> List[Dict]:
    """Fetch jobs based on filters"""
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return []
    
    supabase: Client = current_app.supabase
    
    try:
        # Base query
        query = supabase.table("jobs").select("*, company:companies(*)")
        
        # Apply filters
        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.or_(f"title.ilike.{search_term},description.ilike.{search_term}")
        
        if filters.get("location"):
            query = query.ilike("location", f"%{filters['location']}%")
        
        if filters.get("contract_type"):
            query = query.eq("contract_type", filters["contract_type"])
        
        if filters.get("work_mode"):
            query = query.in_("work_mode", filters["work_mode"])
        
        if filters.get("min_salary"):
            # Assuming salary_range is stored as text like "€50,000 - €60,000"
            # This would need adjustment based on your actual data format
            query = query.gte("salary_range", f"€{filters['min_salary']}")
        
        # Pagination
        page = filters.get("page", 1)
        limit = filters.get("limit", 20)
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        jobs = response.data or []
        
        # Format jobs to match your TypeScript Job type
        formatted_jobs = []
        for job in jobs:
            formatted_job = {
                "id": job["id"],
                "company_id": job["company_id"],
                "title": job["title"],
                "description": job["description"],
                "location": job["location"],
                "requirements": job.get("requirements", []),
                "education": job.get("education", ""),
                "created_at": job["created_at"],
                "company": {
                    "name": job["company"]["name"],
                    "logo_url": job["company"].get("logo_url"),
                    "description": job["company"].get("description", "")
                },
                "contract_type": job.get("contract_type"),
                "work_mode": job.get("work_mode"),
                "salary_range": job.get("salary_range"),
                "skills": job.get("requirements", [])[:5],  # Using requirements as skills for now
                "match_score": calculate_match_score(job, authenticated_uid)  # Implement this
            }
            formatted_jobs.append(formatted_job)
        
        return formatted_jobs
    
    except Exception as e:
        current_app.logger.error(f"Error fetching jobs: {str(e)}")
        return []
def get_job_by_id(job_id: str) -> Optional[Dict]:
    """Fetch a single job by ID with enhanced error handling"""
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        current_app.logger.warning(f"Unauthorized access attempt for job {job_id}")
        return None
    
    supabase: Client = current_app.supabase
    
    try:
        # First fetch the job with company data
        job_query = supabase.table("jobs").select("*, company:companies(*)").eq("id", job_id)
        job_response = job_query.maybe_single().execute()
        
        if not job_response.data:
            current_app.logger.info(f"Job not found: {job_id}")
            return None
            
        job = job_response.data
        
        # Then check application status
        try:
            application_response = supabase.table("applications").select("*").match({
                "job_id": job_id,
                "candidate_id": authenticated_uid
            }).maybe_single().execute()
            
            has_applied = bool(application_response.data)
        except Exception as app_err:
            current_app.logger.error(f"Error checking application status: {str(app_err)}")
            has_applied = False
        
        # Format the job response
        formatted_job = {
            "id": job["id"],
            "company_id": job["company_id"],
            "title": job["title"],
            "description": job["description"],
            "location": job["location"],
            "requirements": job.get("requirements", []),
            "education": job.get("education", ""),
            "created_at": job["created_at"],
            "company": {
                "name": job.get("company", {}).get("name", "Unknown Company"),
                "logo_url": job.get("company", {}).get("logo_url"),
                "description": job.get("company", {}).get("description", "")
            },
            "contract_type": job.get("contract_type"),
            "work_mode": job.get("work_mode"),
            "salary_range": job.get("salary_range"),
            "skills": job.get("skills", job.get("requirements", [])[:5]),
            "has_applied": has_applied,
            "match_score": calculate_match_score(job, authenticated_uid)
        }
        
        return formatted_job
        
    except Exception as e:
        current_app.logger.error(f"Error fetching job {job_id}: {str(e)}", exc_info=True)
        return None

def get_recommended_jobs() -> List[Dict]:
    """Fetch recommended jobs for the current user"""
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return []
    
    supabase: Client = current_app.supabase
    
    try:
        # First get user's skills from profile
        profile_response = supabase.table("candidate_profiles").select(
            "py_skills, skillner_skills, added_skills"
        ).eq("candidate_id", authenticated_uid).single().execute()
        
        profile = profile_response.data or {}
        user_skills = set(
            (profile.get("py_skills", []) or []) +
            (profile.get("skillner_skills", []) or []) +
            (profile.get("added_skills", []) or [])
        )
        
        # Get all jobs (consider adding limits/filters)
        jobs_response = supabase.table("jobs").select("*, company:companies(*)").execute()
        jobs = jobs_response.data or []
        
        # Calculate match scores and filter
        recommended_jobs = []
        for job in jobs:
            job_skills = set(job.get("requirements", [])[:10])  # Using requirements as skills
            common_skills = user_skills.intersection(job_skills)
            match_score = int((len(common_skills) / max(len(job_skills), 1)) * 100)
            
            if match_score >= 50:  # Only recommend if at least 50% match
                formatted_job = {
                    "id": job["id"],
                    "company_id": job["company_id"],
                    "title": job["title"],
                    "description": job["description"],
                    "location": job["location"],
                    "requirements": job.get("requirements", []),
                    "education": job.get("education", ""),
                    "created_at": job["created_at"],
                    "company": {
                        "name": job["company"]["name"],
                        "logo_url": job["company"].get("logo_url"),
                        "description": job["company"].get("description", "")
                    },
                    "contract_type": job.get("contract_type"),
                    "work_mode": job.get("work_mode"),
                    "salary_range": job.get("salary_range"),
                    "skills": list(job_skills),
                    "match_score": match_score,
                    "is_recommended": True
                }
                recommended_jobs.append(formatted_job)
        
        # Sort by match score descending
        recommended_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return recommended_jobs[:20]  # Return top 20
    
    except Exception as e:
        current_app.logger.error(f"Error fetching recommended jobs: {str(e)}")
        return []

def calculate_match_score(job: Dict, candidate_id: str) -> int:
    """Calculate how well a job matches a candidate's profile"""
    # This is a simplified version - you might want to implement a more sophisticated algorithm
    # For now, we'll return a random score between 50-100 for demo purposes
    import random
    return random.randint(50, 100)

def verify_supabase_token():
    """Helper to verify the Supabase token from the request"""
    # Implement your token verification logic here
    # This should extract and verify the JWT from the request headers
    # For now, return a dummy user ID
    return "dummy-user-id"  # Replace with actual implementation