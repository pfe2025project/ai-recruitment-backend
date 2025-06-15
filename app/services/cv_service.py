import datetime
from flask import current_app, request
from werkzeug.utils import secure_filename
from supabase import Client, StorageException

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_supabase_token() -> str | None:
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
    
def update_or_insert_candidate_profile(supabase, uid, public_url):
    # Step 1: Check if profile exists
    existing_profile = supabase.table("candidate_profiles").select("id").eq("candidate_id", uid).execute()

    if existing_profile.data and len(existing_profile.data) > 0:
        # Step 2: Update existing profile
        profile_id = existing_profile.data[0]["id"]
        update_response = supabase.table("candidate_profiles").update({
            "cv_path": public_url,
            "cv_last_updated": datetime.datetime.utcnow().isoformat(),
            "source": "candidate"
        }).eq("id", profile_id).execute()

        if hasattr(update_response, 'error') and update_response.error:
            return {"error": "Failed to update candidate_profiles"}, 500
    else:
        # Step 3: Insert new profile
        insert_response = supabase.table("candidate_profiles").insert({
            "candidate_id": uid,
            "cv_path": public_url,
            "cv_last_updated": datetime.datetime.utcnow().isoformat(),
            "source": "candidate"
        }).execute()

        if hasattr(insert_response, 'error') and insert_response.error:
            return {"error": "Failed to insert into candidate_profiles"}, 500

    return {"success": True}


def upload_cv():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized - valid authentication token required"}, 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return {"error": "Unauthorized - user mismatch"}, 403

    uid = request_uid or authenticated_uid

    if 'cv' not in request.files:
        return {"error": "No file part in the request"}, 400

    file = request.files['cv']
    if file.filename == '':
        return {"error": "No file selected"}, 400

    if not allowed_file(file.filename):
        return {"error": "Invalid file type, only PDF/DOC/DOCX allowed"}, 400

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

        supabase.storage.from_("cvs").upload(
            path=filename,
            file=file_content,
            file_options={
                "content-type": file.mimetype,
                "x-upsert": "true"
            }
        )

        public_url = supabase.storage.from_("cvs").get_public_url(filename)

        update_response = supabase.table("candidates").update({"cv_url": public_url}).eq("id", uid).execute()
        if hasattr(update_response, 'error') and update_response.error:
            return {"error": "Failed to update Supabase candidates DB"}, 500

        result = update_or_insert_candidate_profile(supabase, uid, public_url)
        if "error" in result:
            return result, 500


        return {"success": True, "url": public_url}, 200

    except StorageException as e:
        current_app.logger.error(f"Storage error during CV upload: {str(e)}")
        return {"error": "Failed to upload file to storage"}, 500
    except Exception as e:
        current_app.logger.error(f"CV upload error: {str(e)}", exc_info=True)
        return {"error": "Internal server error"}, 500

def get_cv():
    if request.method == "OPTIONS":
        return {}, 200

    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized"}, 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return {"error": "Unauthorized - user mismatch"}, 403

    uid = authenticated_uid
    supabase: Client = current_app.supabase

    try:
        response = supabase.table("candidates").select("cv_url").eq("id", uid).limit(1).execute()
        if hasattr(response, 'error') and response.error:
            return {"error": "Error retrieving CV URL"}, 500

        data = response.data[0] if response.data else None
        if not data or not data.get("cv_url"):
            return {"error": "CV not found"}, 404

        return {"cv_url": data["cv_url"]}, 200
    except Exception as e:
        current_app.logger.error(f"Error getting CV: {str(e)}")
        return {"error": "Internal server error"}, 500

def delete_cv():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized"}, 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return {"error": "Unauthorized - user mismatch"}, 403

    uid = authenticated_uid
    supabase: Client = current_app.supabase

    try:
        response = supabase.table("candidates").select("cv_url").eq("id", uid).limit(1).execute()
        if hasattr(response, 'error') and response.error:
            return {"error": "Failed to retrieve CV URL"}, 500

        data = response.data[0] if response.data else None
        if not data or not data.get("cv_url"):
            return {"error": "CV not found"}, 404

        public_url = data["cv_url"]
        try:
            filename = public_url.split("/storage/v1/object/public/cvs/")[1]
        except IndexError:
            return {"error": "Invalid file path"}, 400

        supabase.storage.from_("cvs").remove([filename])

        supabase.table("candidates").update({"cv_url": None}).eq("id", uid).execute()
        supabase.table("candidate_profiles").update({"cv_path": None}).eq("candidate_id", uid).execute()

        return {"success": True}, 200

    except StorageException as e:
        current_app.logger.error(f"Storage error during CV deletion: {str(e)}")
        return {"error": "Failed to delete file from storage"}, 500
    except Exception as e:
        current_app.logger.error(f"CV deletion error: {str(e)}")
        return {"error": "Internal server error"}, 500

def check_cv_uploaded():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized"}, 401

    request_uid = request.args.get("uid")
    if request_uid and request_uid != authenticated_uid:
        return {"error": "Unauthorized - user mismatch"}, 403

    uid = authenticated_uid
    supabase: Client = current_app.supabase

    try:
        candidate_response = supabase.table("candidates").select("cv_url").eq("id", uid).limit(1).execute()
        if hasattr(candidate_response, 'error') and candidate_response.error:
            return {"error": "Error querying candidates table"}, 500

        candidate_data = candidate_response.data[0] if candidate_response.data else {}
        cv_uploaded = bool(candidate_data.get("cv_url"))

        return {"cv_uploaded": cv_uploaded}, 200
    except Exception as e:
        current_app.logger.error(f"Error checking CV status: {str(e)}")
        return {"error": "Internal server error"}, 500



# ===== CV LAST UPDATED =====
def get_cv_last_updated():
    authenticated_uid = verify_supabase_token()
    if not authenticated_uid:
        return {"error": "Unauthorized"}, 401

    supabase: Client = current_app.supabase
    
    try:
        response = supabase.table("candidates").select("cv_last_updated").eq("id", authenticated_uid).single().execute()
        return {"cv_last_updated": response.data.get("cv_last_updated")}, 200
    except Exception as e:
        current_app.logger.error(f"Error getting CV last updated: {str(e)}")
        return {"error": "Internal server error"}, 500


