"""
Blueprint pro fact-checking funkcionalitu.

Tento modul obsahuje routy pro fact-checking funkcionalitu aplikace.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from models import db, Analysis
from services import OpenAIService

factcheck_bp = Blueprint('factcheck', __name__)

@factcheck_bp.route('/')
def index():
    return render_template('factcheck/index.html')

@factcheck_bp.route('/analyze', methods=['POST'])
def analyze():
    claim_text = request.form.get('claim_text', '')
    analysis_type = request.form.get('analysis_type', 'standard')

    if not claim_text:
        flash('Zadejte tvrzení k ověření.', 'error')
        return redirect(url_for('factcheck.index'))

    openai_service = None
    try:
        openai_api_key = current_app.config['OPENAI_API_KEY']
        openai_model = current_app.config['OPENAI_MODEL']
        openai_api_version = current_app.config.get('OPENAI_API_VERSION')

        if not openai_api_key:
            flash('API klíč není nastaven. Kontaktujte správce aplikace.', 'error')
            return redirect(url_for('factcheck.index'))

        openai_service = OpenAIService(
            api_key=openai_api_key,
            model=openai_model,
            api_version=openai_api_version
        )
    except ValueError as e:
        flash(f'Neplatný API klíč: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))
    except Exception as e:
        flash(f'Chyba při inicializaci OpenAI služby: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))

    try:
        user_id = session.get('user_id')
        result = openai_service.analyze_claim(claim_text, analysis_type)

        if result.get('verdict') == 'nelze ověřit' and result.get('confidence') == 0:
            error_message = result.get('explanation', 'Neznámá chyba při analýze')
            if 'Nepodařilo se provést analýzu' in error_message:
                flash(error_message, 'error')
                return redirect(url_for('factcheck.index'))

        analysis = Analysis.from_openai_response(claim_text, result, analysis_type, user_id)
        db.session.add(analysis)
        db.session.commit()

        return redirect(url_for('factcheck.result', analysis_id=analysis.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Chyba při analýze tvrzení: {str(e)}', 'error')
        return redirect(url_for('factcheck.index'))

@factcheck_bp.route('/result/<int:analysis_id>')
def result(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    return render_template('factcheck/result.html', analysis=analysis)

@factcheck_bp.route('/history')
def history():
    # Implementace historie analýz zde
    pass
