from flask import Blueprint, request, jsonify, current_app
import os
from dotenv import load_dotenv
import time


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        # Validation with user-friendly messages
        if not all([email, password, role]):
            return jsonify({
                "error": "Please fill in all fields",
                "details": "Email, password, and role are required"
            }), 400
            
        if role not in ["candidate", "recruiter"]:
            return jsonify({
                "error": "Invalid account type",
                "details": "Please select either candidate or recruiter"
            }), 400

        # Supabase authentication
        supabase = current_app.supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Verify user exists in role table
        user_id = auth_response.user.id
        table = "candidates" if role == "candidate" else "recruiters"
        exists = supabase.table(table).select("id").eq("id", user_id).execute()

        if not exists.data:
            return jsonify({
                "error": "Account not found",
                "details": f"Please register as a {role} first"
            }), 403

        return jsonify({
            "access_token": auth_response.session.access_token,
            "user": {
                "id": user_id,
                "email": email,
                "role": role
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            "error": "Login failed",
            "details": f"{e}"
        }), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    # Input validation with clear messages
    if not all([email, password, role]):
        return jsonify({
            "error": "Missing required fields",
            "details": "Please provide your email, password, and account type."
        }), 400

    if role not in ("candidate", "recruiter"):
        return jsonify({
            "error": "Invalid account type",
            "details": "Account type must be either 'candidate' or 'recruiter'."
        }), 400

    supabase = current_app.supabase

    try:
        # Check if email already exists FOR THIS SPECIFIC ROLE
        table_name = "candidates" if role == "candidate" else "recruiters"
        existing_entry = supabase.table(table_name).select("id").eq("email", email).execute()
        
        if existing_entry.data:
            return jsonify({
                "error": "Account already exists",
                "details": f"You already have a {role} account with this email."
            }), 409

        # Create new auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })

        if not auth_response.user:
            return jsonify({
                "error": "Registration failed",
                "details": "Could not create your account. Please try again."
            }), 400
        
        user_id = auth_response.user.id

        # Insert user into role-specific table
        supabase.table(table_name).insert({
            "id": user_id, 
            "email": email,
            "created_at": "now()"
        }).execute()
        
        # Get session token
        access_token = None
        if hasattr(auth_response, 'session') and auth_response.session:
            access_token = auth_response.session.access_token
        else:
            # Sign in to get session immediately after sign up
            login_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            access_token = login_response.session.access_token

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "access_token": access_token,
            "user": {
                "id": user_id,
                "email": email,
                "role": role
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            "error": "Server error",
            "details": f"{e}"
        }), 500


@auth_bp.route("/google-callback", methods=["POST"])
def google_callback():
    try:
        data = request.get_json()
        user_data = data.get("user")
        role = data.get("role")
        access_token = data.get("access_token")

        if not all([user_data, role, access_token]):
            return jsonify({
                "error": "Missing required data",
                "details": "User data, role, and access token are required"
            }), 400

        user_id = user_data.get("id")
        email = user_data.get("email")
        full_name = user_data.get("full_name")

        if not all([user_id, email]):
            return jsonify({
                "error": "Invalid user data",
                "details": "User ID and email are required"
            }), 400

        supabase = current_app.supabase
        table_name = "candidates" if role == "candidate" else "recruiters"

        # Check if user already exists in this specific role table
        existing_user = supabase.table(table_name).select("*").eq("id", user_id).execute()

        if not existing_user.data:
            # User doesn't exist in this role table - create the record
            user_record = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "created_at": "now()"
            }
            supabase.table(table_name).insert(user_record).execute()

        return jsonify({
            "success": True,
            "message": "Google authentication successful",
            "access_token": access_token,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": role
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Google callback error: {str(e)}")
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500    
        
  