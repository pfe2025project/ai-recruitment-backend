from flask import Blueprint, request, jsonify
from app.services.matching_service import (
    get_matching_service,
    match_candidate_to_jobs_authenticated,
    get_skill_recommendations_authenticated
)
from app.utils.auth_utils import verify_supabase_token
from flask import Blueprint, jsonify, request, current_app

ai_matching_bp = Blueprint('ai_matching', __name__, url_prefix='/api/ai-matching')

@ai_matching_bp.route('/candidate/jobs', methods=['GET', 'OPTIONS'])
def match_candidate_jobs():

    """
    Match authenticated candidate to jobs using hybrid AI.
    
    Query Parameters:
    - job_ids: Optional comma-separated list of job IDs to match against
    - limit: Maximum number of jobs to return (default: 10)
    
    Returns:
    - List of job matches with hybrid AI scores
    """
    try:
        # Get query parameters
        job_ids_param = request.args.get('job_ids')
        limit = int(request.args.get('limit', 10))
        
        # Parse job IDs if provided
        job_ids = None
        if job_ids_param:
            job_ids = [job_id.strip() for job_id in job_ids_param.split(',') if job_id.strip()]
        
        # Get matches
        result, status_code = match_candidate_to_jobs_authenticated(job_ids, limit)
        return jsonify(result), status_code
        
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400
    except Exception as e:
        current_app.logger.error(f"Error in candidate job matching endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@ai_matching_bp.route('/job/<job_id>/candidates', methods=['GET'])
def match_job_candidates(job_id):
    """
    Match a job to candidates using hybrid AI.
    
    Path Parameters:
    - job_id: UUID of the job
    
    Query Parameters:
    - candidate_ids: Optional comma-separated list of candidate IDs to match against
    - limit: Maximum number of candidates to return (default: 10)
    
    Returns:
    - List of candidate matches with hybrid AI scores
    """
    try:
        # Verify authentication (recruiter access)
        authenticated_uid = verify_supabase_token()
        if not authenticated_uid:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get query parameters
        candidate_ids_param = request.args.get('candidate_ids')
        limit = int(request.args.get('limit', 10))
        
        # Parse candidate IDs if provided
        candidate_ids = None
        if candidate_ids_param:
            candidate_ids = [cid.strip() for cid in candidate_ids_param.split(',') if cid.strip()]
        
        # Get matches
        service = get_matching_service()
        matches = service.match_job_to_candidates(job_id, candidate_ids, limit)
        
        return jsonify({
            "matches": matches,
            "total_matches": len(matches),
            "job_id": job_id
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400
    except Exception as e:
        current_app.logger.error(f"Error in job candidate matching endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@ai_matching_bp.route('/candidate/skill-recommendations/<job_id>', methods=['GET'])
def get_skill_recommendations(job_id):
    """
    Get skill recommendations for authenticated candidate based on target job.
    
    Path Parameters:
    - job_id: UUID of the target job
    
    Returns:
    - Skill gap analysis and recommendations
    """
    try:
        result, status_code = get_skill_recommendations_authenticated(job_id)
        return jsonify(result), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error in skill recommendations endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@ai_matching_bp.route('/candidate/skills/extract', methods=['POST'])
def extract_skills_from_text():
    """
    Extract skills from provided text using hybrid AI.
    
    Request Body:
    {
        "text": "Text to extract skills from"
    }
    
    Returns:
    - List of extracted skills
    """
    try:
        # Verify authentication
        authenticated_uid = verify_supabase_token()
        if not authenticated_uid:
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Text is required"}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({"error": "Text cannot be empty"}), 400
        
        # Extract skills using hybrid AI
        service = get_matching_service()
        extracted_skills = service.hybrid_ai.extract_skills_dict(text)
        
        return jsonify({
            "extracted_skills": extracted_skills,
            "skills_count": len(extracted_skills),
            "text_length": len(text)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in skill extraction endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@ai_matching_bp.route('/similarity/calculate', methods=['POST'])
def calculate_similarity():
    """
    Calculate similarity between two texts using hybrid AI.
    
    Request Body:
    {
        "text1": "First text (e.g., resume)",
        "text2": "Second text (e.g., job description)"
    }
    
    Returns:
    - Hybrid similarity score and component scores
    """
    try:
        # Verify authentication
        authenticated_uid = verify_supabase_token()
        if not authenticated_uid:
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        if not data or 'text1' not in data or 'text2' not in data:
            return jsonify({"error": "Both text1 and text2 are required"}), 400
        
        text1 = data['text1']
        text2 = data['text2']
        
        if not text1.strip() or not text2.strip():
            return jsonify({"error": "Texts cannot be empty"}), 400
        
        # Calculate similarity using hybrid AI
        service = get_matching_service()
        similarity_result = service.hybrid_ai.calculate_hybrid_score(text1, text2)
        
        return jsonify(similarity_result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in similarity calculation endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@ai_matching_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for AI matching service.
    Tests the AI models and matching functionality with dummy data.
    
    Returns:
    - Status of AI models and services
    """
    try:
        service = get_matching_service()
        
        # Dummy CV and Job data for testing
        dummy_cv_text = "Experienced software engineer with strong Python and machine learning skills."
        dummy_job_text = "Looking for a Python developer with experience in AI and Flask."
        
        # Test hybrid AI score calculation
        try:
            test_score_result = service.hybrid_ai.calculate_hybrid_score(dummy_cv_text, dummy_job_text)
            if not test_score_result or 'hybrid_score' not in test_score_result:
                raise ValueError("Hybrid AI score calculation returned invalid result.")
            
            # Test skill extraction
            test_skills_cv = service.hybrid_ai.extract_skills_dict(dummy_cv_text)
            test_skills_job = service.hybrid_ai.extract_skills_dict(dummy_job_text)
            
            if not isinstance(test_skills_cv, dict) or not isinstance(test_skills_job, dict):
                raise ValueError("Skill extraction returned invalid result.")

            return jsonify({
                "status": "ok",
                "message": "AI models and matching service are operational.",
                "test_results": {
                    "hybrid_score_calculation": "success",
                    "dummy_score": test_score_result['hybrid_score'],
                    "skill_extraction": "success",
                    "extracted_skills_cv_count": len(test_skills_cv),
                    "extracted_skills_job_count": len(test_skills_job)
                }
            }), 200
            
        except Exception as ai_test_e:
            current_app.logger.error(f"AI model health check failed: {str(ai_test_e)}")
            return jsonify({
                "status": "error",
                "message": "AI models or matching service failed internal tests.",
                "details": str(ai_test_e)
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in AI matching health check endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error during health check.",
            "details": str(e)
        }), 500
        # Check if models are loaded
        models_status = {
            "sbert_model": service.hybrid_ai.sbert_model is not None,
            "skill2vec_model": service.hybrid_ai.skill2vec_model is not None,
            "nlp_model": service.hybrid_ai.nlp is not None,
            "skills_dictionary": service.hybrid_ai.skills_dict is not None and len(service.hybrid_ai.skills_dict) > 0
        }
        
        all_models_loaded = all(models_status.values())
        
        return jsonify({
            "status": "healthy" if all_models_loaded else "degraded",
            "models": models_status,
            "skills_count": len(service.hybrid_ai.skills_dict) if service.hybrid_ai.skills_dict else 0,
            "message": "All AI models loaded successfully" if all_models_loaded else "Some AI models failed to load"
        }), 200 if all_models_loaded else 503
        
    except Exception as e:
        current_app.logger.error(f"Error in AI matching health check: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# Error handlers
@ai_matching_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@ai_matching_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@ai_matching_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
