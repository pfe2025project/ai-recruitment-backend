from flask import Blueprint, request, jsonify
from app.services.application_service import *

application_bp = Blueprint("application", __name__)

@application_bp.route("", methods=["POST"])
def handle_create_application():
    response, status = create_application()
    return jsonify(response), status

@application_bp.route("/<application_id>", methods=["PUT"])
def handle_update_application(application_id):
    response, status = update_application(application_id)
    return jsonify(response), status


@application_bp.route("/candidate/<user_id>", methods=["GET"])
def handle_get_user_applications(user_id):
    response, status = get_user_applications(user_id)
    return jsonify(response), status

@application_bp.route("/job/<job_id>", methods=["GET"])
def handle_get_job_applications(job_id):
    response, status = get_job_applications(job_id)
    return jsonify(response), status

@application_bp.route("/<application_id>", methods=["GET"])
def handle_get_application(application_id):
    response, status = get_application(application_id)
    return jsonify(response), status



@application_bp.route("/<application_id>", methods=["DELETE"])
def handle_delete_application(application_id):
    response, status = delete_application(application_id)
    return jsonify(response), status


