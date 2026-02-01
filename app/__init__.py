from flask import Flask, render_template
from instance.config import config
from sqlalchemy.orm import joinedload

from app.extensions import db, login_manager, migrate
from app.utils.custom_filters import register_filters


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object(config[config_name])
    print(
        f"DEBUG: SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register custom Jinja filters
    register_filters(app)

    # Import and register blueprints, user loader, etc. within app context
    with app.app_context():
        from app.models.user import User
        from app.models.role import Role

        # User loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.options(joinedload(User.role).joinedload(
                Role.permissions)).get(int(user_id))

        # Register blueprints
        from app.routes.auth_routes import auth_bp
        from app.routes.admin_routes import admin_bp
        from app.routes.advisor_routes import advisor_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(advisor_bp, url_prefix='/advisor')

        # Index route
        @app.route('/')
        def index():
            return render_template('index.html')

    return app