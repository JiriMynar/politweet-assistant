"""
Blueprint pro sekci podpory projektu.

Tento modul obsahuje routy pro sekci podpory projektu.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, SupporterBenefit

support_bp = Blueprint('support', __name__)

@support_bp.route('/')
def index():
    """Hlavní stránka sekce podpory."""
    return render_template('support/index.html')

@support_bp.route('/monthly')
def monthly():
    """Stránka pro měsíční podporu."""
    # Získání úrovně podpory z parametru URL
    level = request.args.get('level', 'bronze')
    
    # Kontrola, zda je uživatel přihlášen
    if not session.get('user_id'):
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login', next=request.url))
    
    # Zobrazení stránky pro měsíční podporu
    return render_template('support/monthly.html', level=level)

@support_bp.route('/one-time')
def one_time():
    """Stránka pro jednorázovou podporu."""
    # Kontrola, zda je uživatel přihlášen
    if not session.get('user_id'):
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login', next=request.url))
    
    # Zobrazení stránky pro jednorázovou podporu
    return render_template('support/one_time.html')

@support_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """Zpracování platby."""
    # Kontrola, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání dat z formuláře
    payment_type = request.form.get('payment_type')
    amount = request.form.get('amount')
    level = request.form.get('level')
    
    # V reálné aplikaci by zde byla integrace s platební bránou
    # Pro účely demonstrace pouze simulujeme úspěšnou platbu
    
    # Aktualizace uživatele na podporovatele
    try:
        user = User.query.get(user_id)
        
        if payment_type == 'monthly':
            user.is_supporter = True
            user.support_level = level
            flash(f'Děkujeme za vaši měsíční podporu na úrovni {level}!', 'success')
        else:
            flash(f'Děkujeme za váš jednorázový příspěvek ve výši {amount} Kč!', 'success')
        
        db.session.commit()
        
        # Aktualizace session
        session['is_supporter'] = user.is_supporter
        session['support_level'] = user.support_level
        
        return redirect(url_for('support.thank_you'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Chyba při zpracování platby: {str(e)}', 'error')
        return redirect(url_for('support.index'))

@support_bp.route('/thank-you')
def thank_you():
    """Stránka s poděkováním za podporu."""
    return render_template('support/thank_you.html')

@support_bp.route('/cancel')
def cancel():
    """Zrušení podpory."""
    # Kontrola, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro zrušení podpory se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Kontrola, zda je uživatel podporovatelem
    if not session.get('is_supporter'):
        flash('Nejste podporovatelem projektu.', 'error')
        return redirect(url_for('support.index'))
    
    # Zrušení podpory
    try:
        user = User.query.get(user_id)
        user.is_supporter = False
        user.support_level = None
        
        db.session.commit()
        
        # Aktualizace session
        session['is_supporter'] = False
        session['support_level'] = None
        
        flash('Vaše podpora byla úspěšně zrušena.', 'success')
        return redirect(url_for('support.index'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Chyba při zrušení podpory: {str(e)}', 'error')
        return redirect(url_for('support.index'))

@support_bp.route('/benefits')
def benefits():
    """Stránka s výhodami pro podporovatele."""
    # Získání výhod z databáze
    benefits = SupporterBenefit.query.filter_by(is_active=True).all()
    
    # Zobrazení stránky s výhodami
    return render_template('support/benefits.html', benefits=benefits)
