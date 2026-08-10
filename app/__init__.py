from flask import Flask

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

    return app
