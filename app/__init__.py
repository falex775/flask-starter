import os
import logging
from datetime import datetime

from flask import Flask, jsonify, send_from_directory, request

from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(
        __name__, static_folder=os.path.join(os.path.dirname(__file__), "static")
    )
    app.config.from_object(Config)

    # Production logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        supports_credentials=True,
        origins=os.getenv("CORS_ORIGINS", "*").split(","),
    )

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token expired", "message": "Please log in again"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token", "message": str(error)}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Unauthorized", "message": str(error)}), 401

    # Blueprints
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

    # Static / SPA
    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/<path:path>")
    def catch_all(path):
        target = os.path.join(app.static_folder, path)
        if os.path.isfile(target):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {"error": "Not Found", "message": "The requested resource does not exist"}
                ),
                404,
            )
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Unhandled exception")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )

    return app
