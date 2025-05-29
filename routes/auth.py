"""
Blueprint pro autentizaci a správu uživatelů.

Tento modul obsahuje routy pro registraci, přihlášení a správu uživatelských účtů.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not username or not email or not password:
            flash('Všechna pole jsou povinná.', 'error')
            return render_template('auth/register.html')

        if password != password_confirm:
            flash('Hesla se neshodují.', 'error')
            return render_template('auth/register.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Uživatelské jméno již existuje.', 'error')
            return render_template('auth/register.html')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('E-mail již existuje.', 'error')
            return render_template('auth/register.html')

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registrace byla úspěšná. Nyní se můžete přihlásit.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Chyba při registraci: {str(e)}', 'error')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Zadejte uživatelské jméno a heslo.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Neplatné uživatelské jméno nebo heslo.', 'error')
            return render_template('auth/login.html')

        session['user_id'] = user.id
        session['username'] = user.username
        session['is_supporter'] = user.is_supporter
        session['support_level'] = user.support_level

        flash('Přihlášení bylo úspěšné.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_supporter', None)
    session.pop('support_level', None)
    flash('Byli jste odhlášeni.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
def profile():
    # Implementace profilu uživatele zde
    pass
