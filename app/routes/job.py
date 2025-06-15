from flask import Blueprint, jsonify, current_app, request
from app.services.job_services import get_jobs_data, get_job_by_id, get_recommended_jobs

job_bp = Blueprint("job", __name__)

@job_bp.route("", methods=["GET"])
def get_jobs():
    try:
        # Parse query parameters
        search = request.args.get("search")
        location = request.args.get("location")
        contract_type = request.args.get("contract_type")
        work_mode = request.args.getlist("work_mode")
        min_salary = request.args.get("min_salary", type=float)
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)
        
        # Prepare filters dict
        filters = {
            "search": search,
            "location": location,
            "contract_type": contract_type,
            "work_mode": work_mode,
            "min_salary": min_salary,
            "page": page,
            "limit": limit
        }
        
        jobs = get_jobs_data(filters)
        return jsonify({"jobs": jobs}), 200
    except Exception as e:
        current_app.logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@job_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = get_job_by_id(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        return jsonify(job), 200
    except Exception as e:
        current_app.logger.error(f"Error getting job {job_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@job_bp.route("/recommended", methods=["GET"])
def get_recommended():
    try:
        jobs = get_recommended_jobs()
        return jsonify({"jobs": jobs}), 200
    except Exception as e:
        current_app.logger.error(f"Error getting recommended jobs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500