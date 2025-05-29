"""
Hlavní soubor aplikace pro spuštění webového serveru.

Tento soubor slouží jako vstupní bod aplikace.
"""

import os
import sys
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from services import OpenAIService
from models import db  # Importujeme db přímo z models.py

# Nastavení loggeru
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Vytvoření a konfigurace Flask aplikace."""
    app = Flask(__name__)
    
    # Načtení konfigurace
    app.config.from_pyfile('config.py')
    
    # Kontrola, zda je nastaven OpenAI API klíč
    if not app.config.get('OPENAI_API_KEY'):
        logger.warning("VAROVÁNÍ: Proměnná prostředí OPENAI_API_KEY není nastavena. Funkce analýzy tvrzení nebude fungovat.")
    else:
        logger.info(f"OpenAI API klíč je nastaven. Používaný model: {app.config.get('OPENAI_MODEL', 'gpt-4o')}")
    
    # Inicializace databáze s aplikací - používáme instanci z models.py
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
        try:
            db.create_all()
            logger.info("Databázové tabulky byly úspěšně vytvořeny")
        except Exception as e:
            logger.error(f"Chyba při vytváření databázových tabulek: {str(e)}")
    
    # Přidání aktuálního roku do kontextu šablon
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Ošetření chyby 404
    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"Stránka nenalezena: {request.path}")
        return render_template('errors/404.html'), 404
    
    # Ošetření chyby 500
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Interní chyba serveru: {str(e)}")
        return render_template('errors/500.html'), 500
    
    # Přidání OpenAI API klíče do kontextu aplikace
    @app.context_processor
    def inject_openai_status():
        api_key_set = bool(app.config.get('OPENAI_API_KEY'))
        return {'openai_api_key_set': api_key_set}
    
    return app

# Vytvoření aplikace
app = create_app()

if __name__ == '__main__':
    # Kontrola, zda je nastaven OpenAI API klíč
    if not app.config.get('OPENAI_API_KEY'):
        print("VAROVÁNÍ: Proměnná prostředí OPENAI_API_KEY není nastavena.")
        print("Funkce analýzy tvrzení nebude fungovat správně.")
        print("Nastavte proměnnou prostředí OPENAI_API_KEY před spuštěním aplikace.")
    
    # Spuštění aplikace
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
