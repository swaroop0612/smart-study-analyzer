"""
Smart Study Analyzer - Main Flask Application
Entry point for the backend API.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from routes.study_routes import study_bp
from routes.dashboard_routes import dashboard_bp
from routes.coach_routes import coach_bp



def create_app():
    """Application factory pattern — clean and testable."""
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(get_config())
    
    # Enable CORS (so frontend on Vercel can call this API)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(study_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(coach_bp)

    
    # Health check route
    @app.route("/")
    def home():
        return jsonify({
            "app": app.config["APP_NAME"],
            "version": app.config["APP_VERSION"],
            "status": "running",
            "endpoints": {
                "study": "/api/study/sessions",
                "dashboard": "/api/dashboard/stats",
                "students": "/api/study/students"
            }
        }), 200
    
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
