"""
Blueprint pro sekci podpory projektu.

Tento modul obsahuje routy pro finanční podporu projektu.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.models import db, User, SupporterBenefit

support_bp = Blueprint('support', __name__)

@support_bp.route('/')
def index():
    """Hlavní stránka podpory projektu."""
    # Načtení výhod pro podporovatele
    benefits = {
        'bronze': SupporterBenefit.query.filter_by(support_level='bronze').all(),
        'silver': SupporterBenefit.query.filter_by(support_level='silver').all(),
        'gold': SupporterBenefit.query.filter_by(support_level='gold').all(),
        'platinum': SupporterBenefit.query.filter_by(support_level='platinum').all()
    }
    
    return render_template('support/index.html', benefits=benefits)

@support_bp.route('/one-time')
def one_time():
    """Stránka pro jednorázové příspěvky."""
    return render_template('support/one_time.html')

@support_bp.route('/monthly')
def monthly():
    """Stránka pro pravidelné měsíční příspěvky."""
    return render_template('support/monthly.html')

@support_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """
    Zpracování platby.
    
    Tato funkce by v reálné aplikaci zpracovala platbu přes platební bránu.
    Pro účely demonstrace pouze simuluje úspěšnou platbu.
    """
    # Kontrola přihlášení
    if 'user_id' not in session:
        flash('Pro podporu projektu se musíte přihlásit.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    # Získání dat z formuláře
    payment_type = request.form.get('payment_type')  # 'one-time' nebo 'monthly'
    amount = request.form.get('amount')
    support_level = request.form.get('support_level')
    
    # Validace dat
    if not payment_type or not amount or not support_level:
        flash('Vyplňte všechna povinná pole.', 'error')
        if payment_type == 'one-time':
            return redirect(url_for('support.one_time'))
        else:
            return redirect(url_for('support.monthly'))
    
    try:
        amount = float(amount)
    except ValueError:
        flash('Neplatná částka.', 'error')
        if payment_type == 'one-time':
            return redirect(url_for('support.one_time'))
        else:
            return redirect(url_for('support.monthly'))
    
    # Simulace zpracování platby
    # V reálné aplikaci by zde byla integrace s platební bránou
    
    # Aktualizace uživatele
    user = User.query.get(session['user_id'])
    user.is_supporter = True
    user.support_level = support_level
    db.session.commit()
    
    # Aktualizace session
    session['is_supporter'] = True
    session['support_level'] = support_level
    
    # Přesměrování na stránku s poděkováním
    flash('Děkujeme za vaši podporu!', 'success')
    return redirect(url_for('support.thank_you'))

@support_bp.route('/thank-you')
def thank_you():
    """Stránka s poděkováním za podporu."""
    return render_template('support/thank_you.html')

@support_bp.route('/benefits')
def benefits():
    """Stránka s výhodami pro podporovatele."""
    # Kontrola přihlášení
    if 'user_id' not in session:
        flash('Pro zobrazení výhod se musíte přihlásit.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    # Kontrola, zda je uživatel podporovatel
    if not session.get('is_supporter'):
        flash('Tato sekce je dostupná pouze pro podporovatele.', 'warning')
        return redirect(url_for('support.index'))
    
    # Načtení výhod pro aktuální úroveň podpory
    support_level = session.get('support_level')
    benefits = SupporterBenefit.query.filter_by(support_level=support_level, is_active=True).all()
    
    return render_template('support/benefits.html', benefits=benefits, support_level=support_level)

@support_bp.route('/supporters')
def supporters():
    """Stránka se seznamem podporovatelů."""
    # Načtení podporovatelů
    supporters = User.query.filter_by(is_supporter=True).all()
    
    return render_template('support/supporters.html', supporters=supporters)

@support_bp.route('/api/payment-methods')
def api_payment_methods():
    """API endpoint pro získání dostupných platebních metod."""
    # V reálné aplikaci by tato data mohla být dynamická
    payment_methods = {
        'card': {
            'name': 'Platební karta',
            'enabled': True
        },
        'bank_transfer': {
            'name': 'Bankovní převod',
            'enabled': True
        },
        'paypal': {
            'name': 'PayPal',
            'enabled': True
        },
        'apple_pay': {
            'name': 'Apple Pay',
            'enabled': True
        },
        'google_pay': {
            'name': 'Google Pay',
            'enabled': True
        }
    }
    
    return jsonify(payment_methods)
