from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config

# Extensions

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models so migrations can detect them
    from . import models  # noqa: F401

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.items import items_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(admin_bp)

    # Lazily seed roles the first time any request is handled (works for Flask>=2 & >=3)
    from .models import UserRole  # local import to avoid circular
    from sqlalchemy.exc import OperationalError

    def _seed_roles():
        if getattr(app, '_roles_seeded', False):
            return
        try:
            if not UserRole.query.filter_by(name='user').first():
                db.session.add(UserRole(name='user'))
            if not UserRole.query.filter_by(name='admin').first():
                db.session.add(UserRole(name='admin'))
            db.session.commit()
            app._roles_seeded = True
        except OperationalError:
            # DB not ready (e.g., during migration commands)
            pass

    @app.before_request
    def seed_roles_if_needed():
        _seed_roles()

    return app
