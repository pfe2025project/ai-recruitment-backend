from flask import Blueprint, request, jsonify
from app.services.cv_service import *
from flask import send_from_directory
from werkzeug.utils import secure_filename

cv_bp = Blueprint("cv", __name__)

@cv_bp.route("", methods=["POST"])  # No trailing slash
@cv_bp.route("/", methods=["POST"])  # With trailing slash
def handle_upload_cv():
    response, status = upload_cv()
    return jsonify(response), status

@cv_bp.route("/", methods=["GET", "OPTIONS"])
def handle_get_cv():
    response, status = get_cv()
    return jsonify(response), status

@cv_bp.route("/", methods=["DELETE"])
def handle_delete_cv():
    response, status = delete_cv()
    return jsonify(response), status

@cv_bp.route("/check_cv_uploaded", methods=["GET"])
def handle_check_cv_uploaded():
    response, status = check_cv_uploaded()
    return jsonify(response), status


# ===== CV LAST UPDATED =====
@cv_bp.route("/cv-last-updated", methods=["GET"])
def cv_last_updated():
    response, status = get_cv_last_updated()
    return jsonify(response), status

@cv_bp.route("/download/<filename>", methods=["GET"])
def download_cv(filename):
    try:
        # Ensure the filename is secure to prevent directory traversal attacks
        secure_filename_val = secure_filename(filename)
        # Assuming UPLOAD_FOLDER is configured in current_app.config
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/cvs')
        return send_from_directory(upload_folder, secure_filename_val, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Error serving CV file {filename}: {str(e)}")
        return jsonify({"error": "Could not retrieve file"}), 500



