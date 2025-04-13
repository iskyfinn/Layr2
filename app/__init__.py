# app/__init__.py

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

from app.extensions import db, login_manager
from app.services.enhanced_document_generator import get_enhanced_document_generator
from app.services.architecture_agent import get_architecture_agent

# Load environment variables
load_dotenv()

# Initialize extensions outside of create_app
migrate = Migrate()

def create_app():
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )
    CORS(app)

    # Configuration
    app.secret_key = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///layr.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'pptx', 'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config.setdefault('UPLOAD_FOLDER', 'uploads')

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    # ✅ Import blueprints and route registration now
    from app.routes import main_bp, auth_bp, applications_bp, arb_bp, analytics_bp
    from app.routes.api import api_bp

    # ✅ Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(arb_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # ✅ Register services
    upload_folder = app.config['UPLOAD_FOLDER']
    app.enhanced_document_generator = get_enhanced_document_generator(os.path.join(upload_folder, 'documents'))
    app.architecture_agent = get_architecture_agent(upload_folder)
    print("Registered endpoints:")
    print(app.url_map)

    return app
