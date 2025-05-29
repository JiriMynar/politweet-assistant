"""
Blueprint pro fact-checking funkcionalitu.

Tento modul obsahuje routy pro fact-checking funkcionalitu aplikace.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from models import db, Analysis  # Importujeme db přímo z models.py
from services import OpenAIService

# Nastavení loggeru
logger = logging.getLogger(__name__)

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
        # Použijeme API klíč z konfigurace aplikace místo přímého přístupu k proměnné prostředí
        openai_api_key = current_app.config.get('OPENAI_API_KEY')
        openai_model = current_app.config.get('OPENAI_MODEL', 'gpt-4o')
        
        if not openai_api_key:
            flash('API klíč není nastaven. Kontaktujte správce aplikace.', 'error')
            logger.error("Pokus o analýzu bez nastaveného API klíče")
            return redirect(url_for('factcheck.index'))
        
        logger.info(f"Inicializace OpenAI služby s modelem {openai_model}")
        openai_service = OpenAIService(openai_api_key, model=openai_model)
    except Exception as e:
        flash(f'Chyba při inicializaci OpenAI služby: {str(e)}', 'error')
        logger.error(f"Chyba při inicializaci OpenAI služby: {str(e)}")
        return redirect(url_for('factcheck.index'))
    
    # Analýza tvrzení
    try:
        # Získání uživatele, pokud je přihlášen
        user_id = session.get('user_id')
        
        # Analýza tvrzení pomocí OpenAI API
        logger.info(f"Začátek analýzy tvrzení typu {analysis_type}: {claim_text[:50]}...")
        result = openai_service.analyze_claim(claim_text, analysis_type)
        
        # Kontrola, zda došlo k chybě
        if result.get('error', False):
            error_message = result.get("error_message", "Neznámá chyba")
            flash(f'Chyba při analýze tvrzení: {error_message}', 'error')
            logger.error(f"Chyba při analýze tvrzení: {error_message}")
            return redirect(url_for('factcheck.index'))
        
        # Vytvoření záznamu v databázi
        analysis = Analysis.from_openai_response(claim_text, result, analysis_type, user_id)
        db.session.add(analysis)
        db.session.commit()
        logger.info(f"Analýza úspěšně uložena do databáze s ID {analysis.id}")
        
        # Přesměrování na stránku s výsledkem
        return redirect(url_for('factcheck.result', analysis_id=analysis.id))
    
    except Exception as e:
        flash(f'Chyba při analýze tvrzení: {str(e)}', 'error')
        logger.error(f"Neočekávaná chyba při analýze tvrzení: {str(e)}")
        return redirect(url_for('factcheck.index'))

@factcheck_bp.route('/result/<int:analysis_id>')
def result(analysis_id):
    """Zobrazení výsledku analýzy."""
    # Získání analýzy z databáze
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        logger.info(f"Zobrazení výsledku analýzy ID {analysis_id}")
        return render_template('factcheck/result.html', analysis=analysis)
    except Exception as e:
        flash(f'Chyba při zobrazení výsledku: {str(e)}', 'error')
        logger.error(f"Chyba při zobrazení výsledku analýzy ID {analysis_id}: {str(e)}")
        return redirect(url_for('factcheck.index'))

@factcheck_bp.route('/history')
def history():
    """Zobrazení historie analýz přihlášeného uživatele."""
    # Kontrola, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro zobrazení historie se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání historie analýz
    try:
        analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).all()
        logger.info(f"Zobrazení historie analýz pro uživatele ID {user_id}, počet položek: {len(analyses)}")
        return render_template('factcheck/history.html', analyses=analyses)
    except Exception as e:
        flash(f'Chyba při načítání historie: {str(e)}', 'error')
        logger.error(f"Chyba při načítání historie analýz pro uživatele ID {user_id}: {str(e)}")
        return redirect(url_for('factcheck.index'))

@factcheck_bp.route('/export/<int:analysis_id>/<format>')
def export(analysis_id, format):
    """Export výsledku analýzy do různých formátů."""
    # Kontrola, zda je uživatel přihlášen a je podporovatelem
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro export výsledků se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání analýzy z databáze
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Kontrola, zda analýza patří přihlášenému uživateli
        if analysis.user_id != user_id:
            flash('Nemáte oprávnění k exportu této analýzy.', 'error')
            logger.warning(f"Pokus o neoprávněný export analýzy ID {analysis_id} uživatelem ID {user_id}")
            return redirect(url_for('factcheck.index'))
        
        # Export podle formátu
        if format == 'json':
            # Export do JSON
            logger.info(f"Export analýzy ID {analysis_id} do formátu JSON")
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
    
    except Exception as e:
        flash(f'Chyba při exportu analýzy: {str(e)}', 'error')
        logger.error(f"Chyba při exportu analýzy ID {analysis_id} do formátu {format}: {str(e)}")
        return redirect(url_for('factcheck.index'))
