"""
Blueprint pro sekci podpory projektu.

Tento modul obsahuje routy pro sekci podpory projektu.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, SupporterBenefit

support_bp = Blueprint('support', __name__)

@support_bp.route('/')
def index():
    return render_template('support/index.html')

@support_bp.route('/monthly')
def monthly():
    level = request.args.get('level', 'bronze')
    if not session.get('user_id'):
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login', next=request.url))
    return render_template('support/monthly.html', level=level)

@support_bp.route('/one-time')
def one_time():
    if not session.get('user_id'):
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login', next=request.url))
    return render_template('support/one_time.html')

@support_bp.route('/process-payment', methods=['POST'])
def process_payment():
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro podporu projektu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))

    payment_type = request.form.get('payment_type')
    amount = request.form.get('amount')
    level = request.form.get('level')

    try:
        user = User.query.get(user_id)
        if payment_type == 'monthly':
            user.is_supporter = True
            user.support_level = level
            flash(f'Děkujeme za vaši měsíční podporu na úrovni {level}!', 'success')
        else:
            flash(f'Děkujeme za váš jednorázový příspěvek ve výši {amount} Kč!', 'success')

        db.session.commit()
        session['is_supporter'] = user.is_supporter
        session['support_level'] = user.support_level
        return redirect(url_for('support.thank_you'))

    except Exception as e:
        db.session.rollback()
        flash(f'Chyba při zpracování platby: {str(e)}', 'error')
        return redirect(url_for('support.index'))

@support_bp.route('/thank-you')
def thank_you():
    return render_template('support/thank_you.html')

@support_bp.route('/cancel')
def cancel():
    # Implementace zrušení podpory zde
    pass
