from flask import Blueprint, current_app, request, jsonify
from werkzeug.utils import secure_filename
from supabase import Client, StorageException
import logging

candidate_bp = Blueprint("cv", __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_supabase_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    supabase: Client = current_app.supabase

    try:
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception as e:
        current_app.logger.error(f"Supabase token verification failed: {str(e)}")
        return None

@candidate_bp.route("", methods=["POST"])  # No trailing slash
@candidate_bp.route("/", methods=["POST"])  # With trailing slash
def upload_cv():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return jsonify({"error": "Unauthorized - valid authentication token required"}), 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return jsonify({"error": "Unauthorized - user mismatch"}), 403

    uid = request_uid or authenticated_uid

    if 'cv' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['cv']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type, only PDF/DOC/DOCX allowed"}), 400

    extension = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{uid}/cv.{extension}")
    supabase: Client = current_app.supabase

    try:
        # Try to delete existing file if it exists
        try:
            existing_files = supabase.storage.from_("cvs").list(uid)
            if any(f['name'] == f"cv.{extension}" for f in existing_files):
                supabase.storage.from_("cvs").remove([filename])
        except StorageException as e:
            if "not found" not in str(e).lower():
                current_app.logger.warning(f"Error checking/deleting existing file: {str(e)}")

        # Read file content and upload
        file_content = file.read()
        
        # Upload the file
        supabase.storage.from_("cvs").upload(
            path=filename,
            file=file_content,
            file_options={
                "content-type": file.mimetype,
                "x-upsert": "true"
            }
        )

        # Get public URL
        public_url = supabase.storage.from_("cvs").get_public_url(filename)

        # Update candidates table
        update_response = supabase.table("candidates").update({"cv_url": public_url}).eq("id", uid).execute()
        if hasattr(update_response, 'error') and update_response.error:
            return jsonify({"error": "Failed to update Supabase candidates DB"}), 500

        # Update candidate_profiles table
        profile_response = supabase.table("candidate_profiles").upsert({
            "candidate_id": uid,
            "cv_path": public_url,
            "source": "candidate"
        }).execute()
        
        if hasattr(profile_response, 'error') and profile_response.error:
            return jsonify({"error": "Failed to update candidate_profiles"}), 500

        return jsonify({"success": True, "url": public_url}), 200

    except StorageException as e:
        current_app.logger.error(f"Storage error during CV upload: {str(e)}")
        return jsonify({"error": "Failed to upload file to storage"}), 500
    except Exception as e:
        current_app.logger.error(f"CV upload error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@candidate_bp.route("/", methods=["GET", "OPTIONS"])
def get_cv():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return jsonify({"error": "Unauthorized"}), 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return jsonify({"error": "Unauthorized - user mismatch"}), 403

    uid = authenticated_uid
    supabase: Client = current_app.supabase

    try:
        response = supabase.table("candidates").select("cv_url").eq("id", uid).limit(1).execute()
        if hasattr(response, 'error') and response.error:
            return jsonify({"error": "Error retrieving CV URL"}), 500

        data = response.data[0] if response.data else None
        if not data or not data.get("cv_url"):
            return jsonify({"error": "CV not found"}), 404

        return jsonify({"cv_url": data["cv_url"]}), 200
    except Exception as e:
        current_app.logger.error(f"Error getting CV: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@candidate_bp.route("/", methods=["DELETE"])
def delete_cv():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return jsonify({"error": "Unauthorized"}), 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return jsonify({"error": "Unauthorized - user mismatch"}), 403

    uid = authenticated_uid
    supabase: Client = current_app.supabase

    try:
        response = supabase.table("candidates").select("cv_url").eq("id", uid).limit(1).execute()
        if hasattr(response, 'error') and response.error:
            return jsonify({"error": "Failed to retrieve CV URL"}), 500

        data = response.data[0] if response.data else None
        if not data or not data.get("cv_url"):
            return jsonify({"error": "CV not found"}), 404

        public_url = data["cv_url"]
        try:
            filename = public_url.split("/storage/v1/object/public/cvs/")[1]
        except IndexError:
            return jsonify({"error": "Invalid file path"}), 400

        # Delete from storage
        supabase.storage.from_("cvs").remove([filename])

        # Update database records
        supabase.table("candidates").update({"cv_url": None}).eq("id", uid).execute()
        supabase.table("candidate_profiles").update({"cv_path": None}).eq("candidate_id", uid).execute()

        return jsonify({"success": True}), 200

    except StorageException as e:
        current_app.logger.error(f"Storage error during CV deletion: {str(e)}")
        return jsonify({"error": "Failed to delete file from storage"}), 500
    except Exception as e:
        current_app.logger.error(f"CV deletion error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@candidate_bp.route("/check_cv_uploaded", methods=["GET"])
def check_cv_uploaded():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return jsonify({"error": "Unauthorized"}), 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return jsonify({"error": "Unauthorized - user mismatch"}), 403

    uid = authenticated_uid
    supabase: Client = current_app.supabase

    try:
        candidate_response = supabase.table("candidates").select("cv_url").eq("id", uid).limit(1).execute()
        if hasattr(candidate_response, 'error') and candidate_response.error:
            return jsonify({"error": "Error querying candidates table"}), 500

        candidate_data = candidate_response.data[0] if candidate_response.data else {}
        cv_uploaded = bool(candidate_data.get("cv_url"))

        return jsonify({"cv_uploaded": cv_uploaded}), 200
    except Exception as e:
        current_app.logger.error(f"Error checking CV status: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500