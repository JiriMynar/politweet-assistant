"""
Blueprint pro vzdělávací obsah.

Tento modul obsahuje routy pro vzdělávací obsah aplikace.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

# Nastavení loggeru
logger = logging.getLogger(__name__)

# Import blueprintu z __init__.py
from routes import education_bp

@education_bp.route('/')
def index():
    """Hlavní stránka vzdělávacího obsahu."""
    logger.info("Zobrazení hlavní stránky vzdělávacího obsahu")
    return render_template('education/index.html')

@education_bp.route('/logical-fallacies')
def logical_fallacies():
    """Stránka s informacemi o logických chybách."""
    logger.info("Zobrazení stránky s informacemi o logických chybách")
    return render_template('education/logical_fallacies.html')

@education_bp.route('/manipulation-techniques')
def manipulation_techniques():
    """Stránka s informacemi o manipulativních technikách."""
    logger.info("Zobrazení stránky s informacemi o manipulativních technikách")
    return render_template('education/manipulation_techniques.html')

@education_bp.route('/fact-checking-guide')
def fact_checking_guide():
    """Stránka s průvodcem fact-checkingem."""
    logger.info("Zobrazení stránky s průvodcem fact-checkingem")
    return render_template('education/fact_checking_guide.html')

@education_bp.route('/resources')
def resources():
    """Stránka s dalšími zdroji."""
    logger.info("Zobrazení stránky s dalšími zdroji")
    return render_template('education/resources.html')
