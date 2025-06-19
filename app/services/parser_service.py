from flask import current_app, request
from supabase import Client
import json
from datetime import datetime
from .cv_service import verify_supabase_token

def extract_skills(text):
    """
    Extrait les compétences depuis un texte brut avec SkillNER.
    Retourne une liste d'objets contenant des informations sur chaque compétence.
    """
    skill_extractor = current_app.skill_extractor
    SKILL_DB=current_app.SKILL_DB
    annotations = skill_extractor.annotate(text)
    skills = []

    # Parcourir les résultats pour tous les types de matching
    # current_app.logger.error(text)

    for type_matching, arr_skills in annotations["results"].items():
        for skill in arr_skills:
            # Récupérer le nom de la compétence à partir de l'id
            if skill['skill_id'] in SKILL_DB:
                skill_name = SKILL_DB[skill['skill_id']]['skill_name']
                current_app.logger.error(skill_name)
                skills.append(skill_name)

    
    return skills

def filter_non_empty(data: dict):
    return {k: v for k, v in data.items() if v not in ("", None, [], {}, "[]", "{}")}



def extract_profile_data():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized"}, 401

    supabase: Client = current_app.supabase
    
    try:
        # Get CV URL
        response = supabase.table("candidate_profiles").select("cv").eq("candidate_id", authenticated_uid).execute()
        cv = response.data[0].get("cv") if response.data else ""

        
        if not cv:
            return {"error": "CV not found"}, 404
        
        # extract skills with skillner 
        skillner_skills = extract_skills(cv)


        
        # Mock response for male candidate matching both TypeScript and DB structure
        # this parsed data will coming from a function 
        parsed_data = {
            "name": "",
            "title": "",
            "location": "",
            "avatarUrl": "",
            "about": "",
            "experiences": [
                {
                    "title": "",
                    "company": "",
                    "period": "",
                    "location": "",
                    "description": ""
                }
            ],
            "education": [
                {
                    "degree": "",
                    "institution": "",
                    "period": "",
                    "location": "",
                    "description": ""
                }
            ],
            "skills": {
                "extracted": {
                    "pySkills": [],
                    "skillnerSkills": skillner_skills
                },
                "added": []
            },
            "languages": [
                {"name": "", "proficiency": ""}
            ],
            "certifications": [
                {
                    "name": "",
                    "issuingBody": "",
                    "issueDate": "",
                    "credentialUrl": ""
                }
            ],
            "jobPreferences": {
                "isAvailable": True,
                "jobType": "",
                "preferredLocation": "",
                "noticePeriod": ""
            },
            "contact": {
                "email": "",
                "phone": "",
                "linkedin": "",
                "website": "",
                "github": ""
            },
            "cvLastUpdated": datetime.now().isoformat(),
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
        
        
        # candidate  updates
        candidates_update = {
            "full_name": parsed_data.get("name", ""),
            "phone": parsed_data.get("contact", {}).get("phone", ""),
        }

        # Filtrer les valeurs non vides
        filtered_candidates_update = filter_non_empty(candidates_update)

        if filtered_candidates_update:
            supabase.table("candidates") \
                    .update(filtered_candidates_update) \
                    .eq("id", authenticated_uid) \
                    .execute()
            
        # candidate profile
        # Filtrer les champs non vides
        filtered_profile_updates = filter_non_empty(profile_updates)

        if filtered_profile_updates:
            supabase.table("candidate_profiles") \
                    .update(filtered_profile_updates) \
                    .eq("candidate_id", authenticated_uid) \
                    .execute()
                    
                    
                    
        return {"message": "Profile updated successfully."}, 200

            
    except Exception as e:
        current_app.logger.error(f"Error extracting profile data: {str(e)}")
        return {"error": "Internal server error"}, 500