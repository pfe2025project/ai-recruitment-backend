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
    from .routes.cv import cv_bp
    from .routes.profile import profile_bp
    from .routes.job  import job_bp
    from .routes.parser  import parser_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cv_bp, url_prefix="/cv")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(parser_bp, url_prefix="/parser")
    app.register_blueprint(job_bp, url_prefix="/job")



    return app