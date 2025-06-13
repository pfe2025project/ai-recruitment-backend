from flask import Flask
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Supabase configuration
    app.supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.cv import candidate_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(candidate_bp, url_prefix="/cv")

    return app