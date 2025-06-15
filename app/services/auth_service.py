def sync_user_profile(data, supabase, logger):
    try:
        user_id = data.get("id")
        email = data.get("email")
        role = data.get("role")
        full_name = data.get("full_name")

        if not all([user_id, email, role]):
            return {
                "error": "Données utilisateur manquantes",
                "details": "L'ID utilisateur, l'email et le rôle sont requis pour la synchronisation du profil."
            }, 400

        if role not in ["candidate", "recruiter"]:
            return {
                "error": "Type de compte invalide",
                "details": "Le rôle doit être 'candidate' ou 'recruiter'."
            }, 400

        table_name = "candidates" if role == "candidate" else "recruiters"
        existing_user_response = supabase.table(table_name).select("id").eq("id", user_id).execute()

        if existing_user_response.data:
            return {
                "success": True,
                "message": f"Le profil utilisateur existe déjà dans la table '{table_name}'.",
                "user_id": user_id,
                "role": role
            }, 200
        else:
            user_record = {
                "id": user_id,
                "email": email,
                "created_at": "now()"
            }
            if full_name:
                user_record["full_name"] = full_name

            insert_response = supabase.table(table_name).insert(user_record).execute()

            if insert_response.data:
                return {
                    "success": True,
                    "message": f"Profil utilisateur créé avec succès dans la table '{table_name}'.",
                    "user_id": user_id,
                    "role": role
                }, 201
            else:
                logger.error(f"Erreur d'insertion Supabase pour {table_name}: {insert_response.error}")
                return {
                    "error": "Échec de la création du profil dans la base de données",
                    "details": insert_response.error.message if insert_response.error else "Erreur de base de données inconnue"
                }, 500

    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation du profil: {str(e)}")
        return {
            "error": "Erreur serveur lors de la synchronisation du profil",
            "details": str(e)
        }, 500


def handle_google_callback(data, supabase, logger):
    try:
        user_data = data.get("user")
        role = data.get("role")
        access_token = data.get("access_token")

        if not all([user_data, role, access_token]):
            return {
                "error": "Missing required data",
                "details": "User data, role, and access token are required"
            }, 400

        user_id = user_data.get("id")
        email = user_data.get("email")
        full_name = user_data.get("full_name")

        if not all([user_id, email]):
            return {
                "error": "Invalid user data",
                "details": "User ID and email are required"
            }, 400

        table_name = "candidates" if role == "candidate" else "recruiters"
        existing_user = supabase.table(table_name).select("*").eq("id", user_id).execute()

        if not existing_user.data:
            user_record = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "created_at": "now()"
            }
            supabase.table(table_name).insert(user_record).execute()

        return {
            "success": True,
            "message": "Google authentication successful",
            "access_token": access_token,
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": role
            }
        }, 200

    except Exception as e:
        logger.error(f"Google callback error: {str(e)}")
        return {
            "error": "Server error",
            "details": str(e)
        }, 500
