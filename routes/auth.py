"""
Blueprint pro autentizaci uživatelů.

Tento modul obsahuje routy pro autentizaci uživatelů.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Import blueprintu z __init__.py
from routes import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení uživatele."""
    if request.method == 'POST':
        # Získání dat z formuláře
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Kontrola, zda byly zadány všechny údaje
        if not email or not password:
            flash('Zadejte e-mail a heslo.', 'error')
            return render_template('auth/login.html')
        
        # Vyhledání uživatele v databázi
        user = User.query.filter_by(email=email).first()
        
        # Kontrola, zda uživatel existuje a heslo je správné
        if not user or not check_password_hash(user.password_hash, password):
            flash('Nesprávný e-mail nebo heslo.', 'error')
            logger.warning(f"Neúspěšný pokus o přihlášení pro e-mail: {email}")
            return render_template('auth/login.html')
        
        # Přihlášení uživatele
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_supporter'] = user.is_supporter
        
        logger.info(f"Uživatel {user.username} (ID: {user.id}) se úspěšně přihlásil")
        flash(f'Vítejte zpět, {user.username}!', 'success')
        return redirect(url_for('main.index'))
    
    # GET požadavek - zobrazení přihlašovacího formuláře
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrace nového uživatele."""
    if request.method == 'POST':
        # Získání dat z formuláře
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Kontrola, zda byly zadány všechny údaje
        if not username or not email or not password or not password_confirm:
            flash('Vyplňte všechny údaje.', 'error')
            return render_template('auth/register.html')
        
        # Kontrola, zda se hesla shodují
        if password != password_confirm:
            flash('Hesla se neshodují.', 'error')
            return render_template('auth/register.html')
        
        # Kontrola, zda uživatelské jméno nebo e-mail již existují
        if User.query.filter_by(username=username).first():
            flash('Uživatelské jméno již existuje.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
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
            logger.info(f"Nový uživatel {username} (ID: {new_user.id}) byl úspěšně zaregistrován")
            
            # Automatické přihlášení po registraci
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['is_supporter'] = new_user.is_supporter
            
            flash('Registrace byla úspěšná!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Chyba při registraci uživatele {username}: {str(e)}")
            flash('Při registraci došlo k chybě. Zkuste to prosím znovu.', 'error')
            return render_template('auth/register.html')
    
    # GET požadavek - zobrazení registračního formuláře
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Odhlášení uživatele."""
    # Získání uživatelského jména před odhlášením pro log
    username = session.get('username', 'Neznámý uživatel')
    user_id = session.get('user_id', 'Neznámé ID')
    
    # Odstranění dat ze session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_supporter', None)
    
    logger.info(f"Uživatel {username} (ID: {user_id}) se odhlásil")
    flash('Byli jste úspěšně odhlášeni.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
def profile():
    """Profil uživatele."""
    # Kontrola, zda je uživatel přihlášen
    if 'user_id' not in session:
        flash('Pro zobrazení profilu se musíte přihlásit.', 'error')
        return redirect(url_for('auth.login'))
    
    # Získání uživatele z databáze
    user = User.query.get(session['user_id'])
    
    if not user:
        # Pokud uživatel neexistuje, odhlásíme ho
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('is_supporter', None)
        
        flash('Váš účet nebyl nalezen.', 'error')
        return redirect(url_for('auth.login'))
    
    logger.info(f"Uživatel {user.username} (ID: {user.id}) zobrazil svůj profil")
    return render_template('auth/profile.html', user=user)
