from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(__name__)
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
    from app.cli import seed, import_contacts
    app.cli.add_command(seed)
    app.cli.add_command(import_contacts)

    # Register root index route
    @app.get("/")
    def index():
        return jsonify({
            "message": "CRM API is running",
            "version": "1.0",
            "health": "/api/health"
        })

    # Register 404 error handler
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

    return app
