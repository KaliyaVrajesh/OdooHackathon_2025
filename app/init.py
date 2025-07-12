from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

def register_blueprints(app):
    """Register all blueprints with the application"""
    from app.routes import main_bp, auth_bp, profile_bp, swaps_bp
    
    app.register_blueprint(main_bp)        # Added missing main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(swaps_bp)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from app.models import User
    return User.query.get(int(user_id))
