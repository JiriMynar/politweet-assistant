"""
Blueprint pro hlavní stránky aplikace.

Tento modul obsahuje routy pro hlavní stránky aplikace.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Import blueprintu z __init__.py
from routes import main_bp

@main_bp.route('/')
def index():
    """Hlavní stránka aplikace."""
    logger.info("Zobrazení hlavní stránky")
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Stránka O nás."""
    logger.info("Zobrazení stránky O nás")
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Kontaktní stránka."""
    logger.info("Zobrazení kontaktní stránky")
    return render_template('contact.html')

@main_bp.route('/terms')
def terms():
    """Stránka s podmínkami použití."""
    logger.info("Zobrazení stránky s podmínkami použití")
    return render_template('terms.html')

@main_bp.route('/privacy')
def privacy():
    """Stránka s ochranou osobních údajů."""
    logger.info("Zobrazení stránky s ochranou osobních údajů")
    return render_template('privacy.html')
