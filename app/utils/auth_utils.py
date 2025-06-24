from flask import request, current_app
from supabase import Client

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