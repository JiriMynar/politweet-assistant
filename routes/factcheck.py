"""
Blueprint pro fact-checking funkcionalitu.

Tento modul obsahuje routy pro fact-checking funkcionalitu aplikace.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from models import db, Analysis
from services import OpenAIService
import os

factcheck_bp = Blueprint('factcheck', __name__)

@factcheck_bp.route('/')
def index():
    """Stránka pro zadání tvrzení k ověření."""
    return render_template('factcheck/index.html')

@factcheck_bp.route('/analyze', methods=['POST'])
def analyze():
    """Zpracování požadavku na analýzu tvrzení."""
    # Získání dat z formuláře
    claim_text = request.form.get('claim_text', '')
    analysis_type = request.form.get('analysis_type', 'standard')
    
    # Kontrola, zda bylo zadáno tvrzení
    if not claim_text:
        flash('Zadejte tvrzení k ověření.', 'error')
        return redirect(url_for('factcheck.index'))
    
    # Získání OpenAI služby
    openai_service = None
    try:
        # Načtení konfigurace z aplikace
        openai_api_key = current_app.config['OPENAI_API_KEY']
        openai_model = current_app.config['OPENAI_MODEL']
        openai_api_version = current_app.config.get('OPENAI_API_VERSION')
        
        # Kontrola existence API klíče
        if not openai_api_key:
            flash('API klíč není nastaven. Kontaktujte správce aplikace nebo nastavte OPENAI_API_KEY v .env souboru.', 'error')
            return redirect(url_for('factcheck.index'))
        
        # Inicializace OpenAI služby
        openai_service = OpenAIService(
            api_key=openai_api_key,
            model=openai_model,
            api_version=openai_api_version
        )
    except ValueError as e:
        # Zachycení chyb validace API klíče
        flash(f'Neplatný API klíč: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))
    except Exception as e:
        # Zachycení ostatních chyb
        flash(f'Chyba při inicializaci OpenAI služby: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))
    
    # Analýza tvrzení
    try:
        # Získání uživatele, pokud je přihlášen
        user_id = session.get('user_id')
        
        # Analýza tvrzení pomocí OpenAI API
        result = openai_service.analyze_claim(claim_text, analysis_type)
        
        # Kontrola, zda analýza proběhla úspěšně
        if result.get('verdict') == 'nelze ověřit' and result.get('confidence') == 0:
            error_message = result.get('explanation', 'Neznámá chyba při analýze')
            if 'Nepodařilo se provést analýzu' in error_message:
                flash(error_message, 'error')
                return redirect(url_for('factcheck.index'))
        
        # Vytvoření záznamu v databázi
        analysis = Analysis.from_openai_response(claim_text, result, analysis_type, user_id)
        db.session.add(analysis)
        db.session.commit()
        
        # Přesměrování na stránku s výsledkem
        return redirect(url_for('factcheck.result', analysis_id=analysis.id))
    
    except Exception as e:
        flash(f'Chyba při analýze tvrzení: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))

@factcheck_bp.route('/result/<int:analysis_id>')
def result(analysis_id):
    """Zobrazení výsledku analýzy."""
    # Získání analýzy z databáze
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Zobrazení výsledku
    return render_template('factcheck/result.html', analysis=analysis)

@factcheck_bp.route('/history')
def history():
    """Zobrazení historie analýz přihlášeného uživatele."""
    # Kontrola, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro zobrazení historie se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání historie analýz
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).all()
    
    # Zobrazení historie
    return render_template('factcheck/history.html', analyses=analyses)

@factcheck_bp.route('/export/<int:analysis_id>/<format>')
def export(analysis_id, format):
    """Export výsledku analýzy do různých formátů."""
    # Kontrola, zda je uživatel přihlášen a je podporovatelem
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro export výsledků se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání analýzy z databáze
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Kontrola, zda analýza patří přihlášenému uživateli
    if analysis.user_id != user_id:
        flash('Nemáte oprávnění k exportu této analýzy.', 'error')
        return redirect(url_for('factcheck.index'))
    
    # Export podle formátu
    if format == 'json':
        # Export do JSON
        data = {
            'claim_text': analysis.claim_text,
            'verdict': analysis.verdict,
            'confidence': analysis.confidence,
            'explanation': analysis.explanation,
            'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat(),
            'evidences': [{'text': evidence.text} for evidence in analysis.evidences],
            'sources': [{'text': source.text, 'url': source.url} for source in analysis.sources],
            'logical_fallacies': [{'text': fallacy.text, 'type': fallacy.type} for fallacy in analysis.logical_fallacies],
            'manipulation_techniques': [{'text': technique.text, 'type': technique.type} for technique in analysis.manipulation_techniques]
        }
        return jsonify(data)
    
    elif format == 'pdf':
        # Export do PDF
        # V reálné aplikaci by zde byla logika pro generování PDF
        flash('Export do PDF není momentálně k dispozici.', 'error')
        return redirect(url_for('factcheck.result', analysis_id=analysis.id))
    
    elif format == 'docx':
        # Export do DOCX
        # V reálné aplikaci by zde byla logika pro generování DOCX
        flash('Export do DOCX není momentálně k dispozici.', 'error')
        return redirect(url_for('factcheck.result', analysis_id=analysis.id))
    
    else:
        flash(f'Neplatný formát exportu: {format}', 'error')
        return redirect(url_for('factcheck.result', analysis_id=analysis.id))
