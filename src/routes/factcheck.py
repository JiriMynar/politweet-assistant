"""
Blueprint pro fact-checking funkcionalitu.

Tento modul obsahuje routy pro fact-checking.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from src.models import db, Analysis
from src.services import OpenAIService
import os

factcheck_bp = Blueprint('factcheck', __name__)

@factcheck_bp.route('/')
def index():
    """Hlavní stránka fact-checkingu."""
    return render_template('factcheck/index.html')

@factcheck_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Zpracování požadavku na analýzu tvrzení.
    
    Přijímá POST požadavek s tvrzením k analýze a volá OpenAI API
    pro získání výsledku.
    """
    # Získání dat z požadavku
    claim_text = request.form.get('claim_text')
    analysis_type = request.form.get('analysis_type', 'standard')
    
    if not claim_text:
        flash('Zadejte tvrzení k analýze.', 'error')
        return redirect(url_for('factcheck.index'))
    
    # Získání OpenAI služby
    openai_service = current_app.config.get('openai_service')
    if not openai_service:
        # Pokud služba není v konfiguraci, vytvoříme novou instanci
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            flash('API klíč OpenAI není nastaven. Kontaktujte správce.', 'error')
            return redirect(url_for('factcheck.index'))
        
        try:
            openai_service = OpenAIService(api_key)
        except Exception as e:
            flash(f'Chyba při inicializaci OpenAI služby: {str(e)}', 'error')
            return redirect(url_for('factcheck.index'))
    
    # Analýza tvrzení
    try:
        result = openai_service.analyze_claim(claim_text, analysis_type)
        
        # Vytvoření záznamu v databázi
        analysis = Analysis.from_openai_response(
            claim_text=claim_text,
            response=result,
            analysis_type=analysis_type,
            user_id=session.get('user_id')
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Přesměrování na stránku s výsledkem
        return redirect(url_for('factcheck.result', analysis_id=analysis.id))
    
    except Exception as e:
        flash(f'Chyba při analýze tvrzení: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))

@factcheck_bp.route('/result/<int:analysis_id>')
def result(analysis_id):
    """
    Zobrazení výsledku analýzy.
    
    Args:
        analysis_id: ID analýzy k zobrazení
    """
    # Načtení analýzy z databáze
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Předání dat do šablony
    return render_template('factcheck/result.html', analysis=analysis)

@factcheck_bp.route('/history')
def history():
    """Zobrazení historie analýz."""
    # Kontrola přihlášení uživatele
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro zobrazení historie se musíte přihlásit.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    # Načtení analýz uživatele
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).all()
    
    # Předání dat do šablony
    return render_template('factcheck/history.html', analyses=analyses)

@factcheck_bp.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API endpoint pro analýzu tvrzení.
    
    Přijímá JSON požadavek s tvrzením k analýze a vrací výsledek
    jako JSON.
    """
    # Kontrola formátu požadavku
    if not request.is_json:
        return jsonify({'error': 'Požadavek musí být ve formátu JSON.'}), 400
    
    # Získání dat z požadavku
    data = request.get_json()
    claim_text = data.get('claim_text')
    analysis_type = data.get('analysis_type', 'standard')
    
    if not claim_text:
        return jsonify({'error': 'Chybí povinný parametr claim_text.'}), 400
    
    # Získání OpenAI služby
    openai_service = current_app.config.get('openai_service')
    if not openai_service:
        # Pokud služba není v konfiguraci, vytvoříme novou instanci
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API klíč OpenAI není nastaven.'}), 500
        
        try:
            openai_service = OpenAIService(api_key)
        except Exception as e:
            return jsonify({'error': f'Chyba při inicializaci OpenAI služby: {str(e)}'}), 500
    
    # Analýza tvrzení
    try:
        result = openai_service.analyze_claim(claim_text, analysis_type)
        
        # Vytvoření záznamu v databázi
        analysis = Analysis.from_openai_response(
            claim_text=claim_text,
            response=result,
            analysis_type=analysis_type,
            user_id=session.get('user_id')
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Vrácení výsledku
        return jsonify({
            'analysis_id': analysis.id,
            'result': result
        })
    
    except Exception as e:
        return jsonify({'error': f'Chyba při analýze tvrzení: {str(e)}'}), 500
