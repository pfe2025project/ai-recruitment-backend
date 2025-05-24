from flask import Blueprint, request, jsonify, current_app
import os
from dotenv import load_dotenv
import time


auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/sync-profile", methods=["POST"])
def sync_profile():
    try:
        data = request.get_json()
        user_id = data.get("id")
        email = data.get("email")
        role = data.get("role")
        full_name = data.get("full_name") # Optionnel, souvent présent pour les utilisateurs OAuth

        # --- Validation des données reçues du frontend ---
        if not all([user_id, email, role]):
            return jsonify({
                "error": "Données utilisateur manquantes",
                "details": "L'ID utilisateur, l'email et le rôle sont requis pour la synchronisation du profil."
            }), 400

        if role not in ["candidate", "recruiter"]:
            return jsonify({
                "error": "Type de compte invalide",
                "details": "Le rôle doit être 'candidate' ou 'recruiter'."
            }), 400

        supabase = current_app.supabase # Accède à l'instance Supabase configurée dans l'application Flask
        table_name = "candidates" if role == "candidate" else "recruiters"

        # --- Vérifier si l'utilisateur existe déjà dans la table de rôle spécifique ---
        # On sélectionne juste l'ID pour vérifier l'existence, c'est plus léger.
        existing_user_response = supabase.table(table_name).select("id").eq("id", user_id).execute()

        if existing_user_response.data:
            # L'utilisateur existe déjà dans cette table de rôle, pas besoin d'insérer.
            # On peut renvoyer un succès avec un message informatif.
            return jsonify({
                "success": True,
                "message": f"Le profil utilisateur existe déjà dans la table '{table_name}'.",
                "user_id": user_id,
                "role": role
            }), 200
        else:
            # L'utilisateur n'existe pas dans cette table de rôle - créer l'enregistrement
            user_record = {
                "id": user_id,
                "email": email,
                # Supabase gère "now()" pour les colonnes de type timestamp avec valeur par défaut
                "created_at": "now()" 
            }
            if full_name: # Ajouter le nom complet si fourni (utile pour les utilisateurs Google)
                user_record["full_name"] = full_name

            insert_response = supabase.table(table_name).insert(user_record).execute()

            # Vérifier si l'insertion a réussi
            if insert_response.data:
                return jsonify({
                    "success": True,
                    "message": f"Profil utilisateur créé avec succès dans la table '{table_name}'.",
                    "user_id": user_id,
                    "role": role
                }), 201 # 201 Created pour une nouvelle ressource
            else:
                # Gérer les erreurs d'insertion de Supabase
                current_app.logger.error(f"Erreur d'insertion Supabase pour {table_name}: {insert_response.error}")
                return jsonify({
                    "error": "Échec de la création du profil dans la base de données",
                    "details": insert_response.error.message if insert_response.error else "Erreur de base de données inconnue"
                }), 500

    except Exception as e:
        # Gestion générale des exceptions
        current_app.logger.error(f"Erreur lors de la synchronisation du profil: {str(e)}")
        return jsonify({
            "error": "Erreur serveur lors de la synchronisation du profil",
            "details": str(e)
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
        
  