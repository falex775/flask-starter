from flask import Flask, jsonify, send_from_directory
import os

from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    from app.routes.contacts import contacts_bp
    from app.routes.deals import deals_bp
    from app.routes.activities import activities_bp
    from app.routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(deals_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(search_bp)

    # Register CLI commands
    #from app.cli import seed, import_contacts
    #app.cli.add_command(seed)
    #app.cli.add_command(import_contacts)

    # Serve static files
    @app.get("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    # Root index route - serve index.html
    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # Catch-all route for SPA navigation - serve index.html for unmapped routes
    @app.get("/<path:path>")
    def catch_all(path):
        # Check if it's a static file request
        if os.path.isfile(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # Otherwise serve index.html for SPA routing
        return send_from_directory(app.static_folder, 'index.html')

    # Register 404 error handler (for API routes that don't match)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource does not exist"
        }), 404

    # Register 500 error handler
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500

    with app.app_context():
        db.create_all()

    return app


