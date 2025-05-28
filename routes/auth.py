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
    """Registrace nového uživatele."""
    if request.method == 'POST':
        # Získání dat z formuláře
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validace dat
        if not username or not email or not password:
            flash('Všechna pole jsou povinná.', 'error')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Hesla se neshodují.', 'error')
            return render_template('auth/register.html')
        
        # Kontrola, zda uživatel již existuje
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Uživatelské jméno již existuje.', 'error')
            return render_template('auth/register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('E-mail již existuje.', 'error')
            return render_template('auth/register.html')
        
        # Vytvoření nového uživatele
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        # Uložení uživatele do databáze
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registrace byla úspěšná. Nyní se můžete přihlásit.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Chyba při registraci: {str(e)}', 'error')
            return render_template('auth/register.html')
    
    # GET požadavek - zobrazení registračního formuláře
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení uživatele."""
    if request.method == 'POST':
        # Získání dat z formuláře
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validace dat
        if not username or not password:
            flash('Zadejte uživatelské jméno a heslo.', 'error')
            return render_template('auth/login.html')
        
        # Vyhledání uživatele
        user = User.query.filter_by(username=username).first()
        
        # Kontrola hesla
        if not user or not check_password_hash(user.password_hash, password):
            flash('Neplatné uživatelské jméno nebo heslo.', 'error')
            return render_template('auth/login.html')
        
        # Přihlášení uživatele
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_supporter'] = user.is_supporter
        session['support_level'] = user.support_level
        
        flash('Přihlášení bylo úspěšné.', 'success')
        return redirect(url_for('main.index'))
    
    # GET požadavek - zobrazení přihlašovacího formuláře
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Odhlášení uživatele."""
    # Odstranění dat ze session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_supporter', None)
    session.pop('support_level', None)
    
    flash('Byli jste odhlášeni.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
def profile():
    """Zobrazení profilu přihlášeného uživatele."""
    # Kontrola, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro zobrazení profilu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání dat uživatele
    user = User.query.get_or_404(user_id)
    
    # Zobrazení profilu
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Úprava profilu přihlášeného uživatele."""
    # Kontrola, zda je uživatel přihlášen
    user_id = session.get('user_id')
    if not user_id:
        flash('Pro úpravu profilu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání dat uživatele
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Získání dat z formuláře
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        new_password_confirm = request.form.get('new_password_confirm')
        
        # Validace e-mailu
        if email and email != user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('E-mail již existuje.', 'error')
                return render_template('auth/edit_profile.html', user=user)
            
            user.email = email
        
        # Změna hesla
        if current_password and new_password:
            # Kontrola současného hesla
            if not check_password_hash(user.password_hash, current_password):
                flash('Nesprávné současné heslo.', 'error')
                return render_template('auth/edit_profile.html', user=user)
            
            # Kontrola nového hesla
            if new_password != new_password_confirm:
                flash('Nová hesla se neshodují.', 'error')
                return render_template('auth/edit_profile.html', user=user)
            
            # Aktualizace hesla
            user.password_hash = generate_password_hash(new_password)
        
        # Uložení změn
        try:
            db.session.commit()
            flash('Profil byl úspěšně aktualizován.', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Chyba při aktualizaci profilu: {str(e)}', 'error')
            return render_template('auth/edit_profile.html', user=user)
    
    # GET požadavek - zobrazení formuláře pro úpravu profilu
    return render_template('auth/edit_profile.html', user=user)
