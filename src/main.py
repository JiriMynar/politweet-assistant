"""
Hlavní modul aplikace.

Tento modul obsahuje hlavní aplikaci Flask a její konfiguraci.
"""

import sys
import os
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

# Přidání cesty pro import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import modelů a služeb
from src.models import db
from src.services import OpenAIService

def create_app():
    """
    Vytvoří a konfiguruje Flask aplikaci.
    
    Returns:
        Flask aplikace
    """
    app = Flask(__name__)
    
    # Konfigurace aplikace
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializace databáze
    db.init_app(app)
    
    # Inicializace OpenAI služby
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    openai_service = None
    if openai_api_key:
        try:
            openai_service = OpenAIService(openai_api_key)
        except Exception as e:
            print(f"Chyba při inicializaci OpenAI služby: {str(e)}")
    
    # Registrace blueprintů
    from src.routes.main import main_bp
    from src.routes.auth import auth_bp
    from src.routes.factcheck import factcheck_bp
    from src.routes.support import support_bp
    from src.routes.education import education_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(factcheck_bp, url_prefix='/factcheck')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(education_bp, url_prefix='/education')
    
    # Vytvoření databázových tabulek
    with app.app_context():
        db.create_all()
    
    # Přidání OpenAI služby do kontextu aplikace
    @app.context_processor
    def inject_openai_service():
        return dict(openai_service=openai_service)
    
    # Ošetření chyb
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, error_message="Stránka nebyla nalezena"), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_code=500, error_message="Interní chyba serveru"), 500
    
    return app

# Vytvoření aplikace
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
