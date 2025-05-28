"""
Blueprint pro autentizaci uživatelů.

Tento modul obsahuje routy pro registraci, přihlášení a správu uživatelů.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení uživatele."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Vyplňte všechna povinná pole.', 'error')
            return render_template('auth/login.html')
        
        # Vyhledání uživatele
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Nesprávný email nebo heslo.', 'error')
            return render_template('auth/login.html')
        
        # Přihlášení uživatele
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_supporter'] = user.is_supporter
        session['support_level'] = user.support_level
        
        # Přesměrování na původní stránku nebo na hlavní stránku
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrace nového uživatele."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not username or not email or not password:
            flash('Vyplňte všechna povinná pole.', 'error')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Hesla se neshodují.', 'error')
            return render_template('auth/register.html')
        
        # Kontrola, zda uživatel již existuje
        if User.query.filter_by(username=username).first():
            flash('Uživatelské jméno je již obsazeno.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email je již registrován.', 'error')
            return render_template('auth/register.html')
        
        # Vytvoření nového uživatele
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrace byla úspěšná. Nyní se můžete přihlásit.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Odhlášení uživatele."""
    session.clear()
    flash('Byli jste úspěšně odhlášeni.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
def profile():
    """Profil uživatele."""
    # Kontrola přihlášení
    if 'user_id' not in session:
        flash('Pro zobrazení profilu se musíte přihlásit.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    # Načtení uživatele
    user = User.query.get_or_404(session['user_id'])
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Úprava profilu uživatele."""
    # Kontrola přihlášení
    if 'user_id' not in session:
        flash('Pro úpravu profilu se musíte přihlásit.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    # Načtení uživatele
    user = User.query.get_or_404(session['user_id'])
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        if not username or not email:
            flash('Vyplňte všechna povinná pole.', 'error')
            return render_template('auth/edit_profile.html', user=user)
        
        # Kontrola, zda uživatelské jméno již existuje
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('Uživatelské jméno je již obsazeno.', 'error')
            return render_template('auth/edit_profile.html', user=user)
        
        # Kontrola, zda email již existuje
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Email je již registrován.', 'error')
            return render_template('auth/edit_profile.html', user=user)
        
        # Aktualizace uživatele
        user.username = username
        user.email = email
        
        db.session.commit()
        
        # Aktualizace session
        session['username'] = user.username
        
        flash('Profil byl úspěšně aktualizován.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=user)

@auth_bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    """Změna hesla uživatele."""
    # Kontrola přihlášení
    if 'user_id' not in session:
        flash('Pro změnu hesla se musíte přihlásit.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    # Načtení uživatele
    user = User.query.get_or_404(session['user_id'])
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        new_password_confirm = request.form.get('new_password_confirm')
        
        if not current_password or not new_password or not new_password_confirm:
            flash('Vyplňte všechna povinná pole.', 'error')
            return render_template('auth/change_password.html')
        
        # Kontrola současného hesla
        if not check_password_hash(user.password_hash, current_password):
            flash('Současné heslo je nesprávné.', 'error')
            return render_template('auth/change_password.html')
        
        # Kontrola nového hesla
        if new_password != new_password_confirm:
            flash('Nová hesla se neshodují.', 'error')
            return render_template('auth/change_password.html')
        
        # Aktualizace hesla
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Heslo bylo úspěšně změněno.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')
