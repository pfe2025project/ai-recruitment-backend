from flask import Blueprint, request, jsonify, current_app
from app.services.auth_service import sync_user_profile, handle_google_callback

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/sync-profile", methods=["POST"])
def sync_profile():
    data = request.get_json()
    result, status = sync_user_profile(data, current_app.supabase, current_app.logger)
    return jsonify(result), status

@auth_bp.route("/google-callback", methods=["POST"])
def google_callback():
    data = request.get_json()
    result, status = handle_google_callback(data, current_app.supabase, current_app.logger)
    return jsonify(result), status
