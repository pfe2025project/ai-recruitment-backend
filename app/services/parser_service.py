from flask import current_app, request
from supabase import Client
import json
from datetime import datetime
from .cv_service import verify_supabase_token

def extract_profile_data():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized"}, 401

    supabase: Client = current_app.supabase
    
    try:
        # Get CV URL
        response = supabase.table("candidates").select("cv_url").eq("id", authenticated_uid).single().execute()
        cv_url = response.data.get("cv_url")
        
        if not cv_url:
            return {"error": "CV not found"}, 404
        
        # Mock response for male candidate matching both TypeScript and DB structure
        parsed_data = {
            "name": "Thomas Martin",
            "title": "Ingénieur Logiciel Senior",
            "location": "Paris, France",
            "avatarUrl": "https://storage.example.com/avatars/thomas-martin.jpg",
            "about": "Ingénieur logiciel avec 8 ans d'expérience en développement backend et architecture cloud. Expert en Python et systèmes distribués.",
            "experiences": [
                {
                    "title": "Architecte Logiciel",
                    "company": "ScaleTech Solutions",
                    "period": "2021-01-01/2023-12-31",
                    "location": "Paris, France",
                    "description": "Conception d'architecture microservices pour plateforme SaaS"
                },
                {
                    "title": "Développeur Backend Senior",
                    "company": "DataSystems France",
                    "period": "2018-06-01/2020-12-31",
                    "location": "Lyon, France",
                    "description": "Développement d'APIs et services backend en Python"
                }
            ],
            "education": [
                {
                    "degree": "Diplôme d'Ingénieur en Informatique",
                    "institution": "École Polytechnique",
                    "period": "2014-09-01/2017-06-30",
                    "location": "Palaiseau, France",
                    "description": "Spécialisation en systèmes distribués"
                }
            ],
            "skills": {
                "extracted": {
                    "pySkills": ["Python", "Django", "FastAPI", "Pandas"],
                    "skillnerSkills": ["AWS", "Docker", "Kubernetes"]
                },
                "added": ["Terraform", "GraphQL", "Redis"]
            },
            "languages": [
                {"name": "Français", "proficiency": "Langue maternelle"},
                {"name": "Anglais", "proficiency": "Courant (TOEIC 920)"}
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuingBody": "Amazon Web Services",
                    "issueDate": "2022-05-20",
                    "credentialUrl": "https://aws.cert/789012"
                }
            ],
            "jobPreferences": {
                "isAvailable": True,
                "jobType": "CDI",
                "preferredLocation": "Paris ou remote",
                "noticePeriod": "1 mois"
            },
            "contact": {
                "email": "thomas.martin@example.com",
                "phone": "+33698765432",
                "linkedin": "linkedin.com/in/thomasmartin",
                "website": "thomasmartin.dev",
                "github": "github.com/tmartin"
            },
            "cvLastUpdated": datetime.now().isoformat(),
            "cvPdfUrl": cv_url
        }
    
    
        profile_updates = {
            "location": parsed_data.get("location", ""),
            "title": parsed_data.get("title", ""),
            "about": parsed_data.get("about", ""),
            "experience": json.dumps( parsed_data.get("experiences", [])),
            "education": json.dumps( parsed_data.get("education", [])),
            "certifications": json.dumps( parsed_data.get("certifications", [])),
            "languages": json.dumps( parsed_data.get("languages", [])),
            "job_preferences": json.dumps( parsed_data.get("jobPreferences", {})),
            "py_skills": parsed_data.get("skills", {}).get("extracted", {}).get("pySkills", []),
            "skillner_skills": parsed_data.get("skills", {}).get("extracted", {}).get("skillnerSkills", []),
            "added_skills": parsed_data.get("skills", {}).get("added", []),
            "linkedin": parsed_data.get("contact", {}).get("linkedin", ""),
            "website": parsed_data.get("contact", {}).get("website", ""),
            "github": parsed_data.get("contact", {}).get("github", ""),
            "updated_at": datetime.now().isoformat()
        }
        
        
        # Update candidates table
        supabase.table("candidates").update({
            "full_name": parsed_data.get("name", ""),
            "phone": parsed_data.get("contact", {}).get("phone", ""),
        }).eq("id", authenticated_uid).execute()
        
            
        
        supabase.table("candidate_profiles") \
                .update(profile_updates) \
                .eq("candidate_id", authenticated_uid) \
                .execute()
        
        return {"success": True, "data": parsed_data}, 200
        
    except Exception as e:
        current_app.logger.error(f"Error extracting profile data: {str(e)}")
        return {"error": "Internal server error"}, 500