from flask_cors import CORS
from app import create_app

app = create_app()

# CORS Configuration (Only configure here - DO NOT add headers in routes)
CORS(
    app,
    resources={
        r"/auth/*": {
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        }
    },
    supports_credentials=True
)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)