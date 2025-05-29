"""
Hlavní soubor aplikace pro spuštění webového serveru.

Tento soubor slouží jako vstupní bod aplikace.
"""

import os
from dotenv import load_dotenv
from flask import Flask, render_template
from datetime import datetime

# Načtení proměnných prostředí z .env souboru (pro lokální vývoj)
load_dotenv()

# SQLAlchemy a modely importujeme pouze z models.py
from models import db

def create_app():
    """Vytvoření a konfigurace Flask aplikace."""
    app = Flask(__name__)

    # Načtení konfigurace
    app.config.from_pyfile('config.py')

    # Inicializace databáze s aplikací
    db.init_app(app)

    # Registrace blueprintů
    from routes import main_bp, auth_bp, factcheck_bp, support_bp, education_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(factcheck_bp, url_prefix='/factcheck')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(education_bp, url_prefix='/education')

    # Vytvoření databázových tabulek
    with app.app_context():
        db.create_all()

    # Přidání aktuálního roku do kontextu šablon
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    # Ošetření chyby 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    # Ošetření chyby 500
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

# Vytvoření aplikace pro server
app = create_app()

if __name__ == '__main__':
    # Spuštění aplikace
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
