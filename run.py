from flask_cors import CORS
from app import create_app

app = create_app()

# CORS Configuration - Updated with correct spelling and broader coverage
CORS(
    app,
    resources={
        r"/auth/*": {
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        },
        r"/cv*": {  
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        },
        r"/profile*": {  
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        },
        r"/parser*": {  
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        },
        r"/job*": {  
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        },
        r"/application*": {  
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 600
        },
        r"/api/ai-matching/*": {  
            "origins": ["http://localhost:3000", "http://192.168.106.1:3000"],
            "methods": ["POST", "PUT", "DELETE", "GET", "OPTIONS"],
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