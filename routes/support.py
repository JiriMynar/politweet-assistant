"""
Blueprint pro podporu projektu.

Tento modul obsahuje routy pro podporu projektu.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, User, SupporterBenefit

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Import blueprintu z __init__.py
from routes import support_bp

@support_bp.route('/')
def index():
    """Stránka s informacemi o podpoře projektu."""
    # Získání úrovní podpory z konfigurace
    support_levels = current_app.config.get('SUPPORT_LEVELS', {})
    
    # Získání výhod podporovatelů z databáze
    benefits = SupporterBenefit.query.filter_by(is_active=True).all()
    
    logger.info("Zobrazení stránky s informacemi o podpoře projektu")
    return render_template('support/index.html', support_levels=support_levels, benefits=benefits)

@support_bp.route('/become-supporter', methods=['GET', 'POST'])
def become_supporter():
    """Stránka pro získání podpory."""
    # Kontrola, zda je uživatel přihlášen
    if 'user_id' not in session:
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání úrovní podpory z konfigurace
    support_levels = current_app.config.get('SUPPORT_LEVELS', {})
    
    if request.method == 'POST':
        # Získání dat z formuláře
        support_level = request.form.get('support_level')
        
        # Kontrola, zda byla vybrána úroveň podpory
        if not support_level or support_level not in support_levels:
            flash('Vyberte platnou úroveň podpory.', 'error')
            return render_template('support/become_supporter.html', support_levels=support_levels)
        
        # Získání uživatele z databáze
        user = User.query.get(session['user_id'])
        
        if not user:
            flash('Váš účet nebyl nalezen.', 'error')
            return redirect(url_for('auth.login'))
        
        # Aktualizace uživatele
        try:
            user.is_supporter = True
            user.support_level = support_level
            db.session.commit()
            
            # Aktualizace session
            session['is_supporter'] = True
            
            logger.info(f"Uživatel {user.username} (ID: {user.id}) se stal podporovatelem na úrovni {support_level}")
            flash(f'Děkujeme za podporu! Nyní jste {support_levels[support_level]["name"]}.', 'success')
            return redirect(url_for('support.thank_you'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Chyba při aktualizaci uživatele {user.username} (ID: {user.id}): {str(e)}")
            flash('Při zpracování vaší podpory došlo k chybě. Zkuste to prosím znovu.', 'error')
            return render_template('support/become_supporter.html', support_levels=support_levels)
    
    # GET požadavek - zobrazení formuláře pro podporu
    return render_template('support/become_supporter.html', support_levels=support_levels)

@support_bp.route('/thank-you')
def thank_you():
    """Stránka s poděkováním za podporu."""
    # Kontrola, zda je uživatel přihlášen a je podporovatelem
    if 'user_id' not in session or not session.get('is_supporter', False):
        return redirect(url_for('support.index'))
    
    # Získání uživatele z databáze
    user = User.query.get(session['user_id'])
    
    if not user or not user.is_supporter:
        return redirect(url_for('support.index'))
    
    # Získání úrovně podpory z konfigurace
    support_level = user.support_level
    support_levels = current_app.config.get('SUPPORT_LEVELS', {})
    support_info = support_levels.get(support_level, {})
    
    logger.info(f"Uživatel {user.username} (ID: {user.id}) zobrazil stránku s poděkováním za podporu")
    return render_template('support/thank_you.html', user=user, support_info=support_info)

@support_bp.route('/cancel', methods=['GET', 'POST'])
def cancel():
    """Stránka pro zrušení podpory."""
    # Kontrola, zda je uživatel přihlášen a je podporovatelem
    if 'user_id' not in session or not session.get('is_supporter', False):
        return redirect(url_for('support.index'))
    
    # Získání uživatele z databáze
    user = User.query.get(session['user_id'])
    
    if not user or not user.is_supporter:
        return redirect(url_for('support.index'))
    
    if request.method == 'POST':
        # Zrušení podpory
        try:
            old_level = user.support_level
            user.is_supporter = False
            user.support_level = None
            db.session.commit()
            
            # Aktualizace session
            session['is_supporter'] = False
            
            logger.info(f"Uživatel {user.username} (ID: {user.id}) zrušil podporu na úrovni {old_level}")
            flash('Vaše podpora byla zrušena. Děkujeme za vaši předchozí podporu!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Chyba při zrušení podpory uživatele {user.username} (ID: {user.id}): {str(e)}")
            flash('Při zrušení vaší podpory došlo k chybě. Zkuste to prosím znovu.', 'error')
            return render_template('support/cancel.html', user=user)
    
    # GET požadavek - zobrazení formuláře pro zrušení podpory
    return render_template('support/cancel.html', user=user)
