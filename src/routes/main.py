"""
Hlavní blueprint pro základní stránky aplikace.

Tento modul obsahuje routy pro hlavní stránky aplikace.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from src.services import OpenAIService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Hlavní stránka aplikace."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Stránka o projektu."""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Kontaktní stránka."""
    return render_template('contact.html')

@main_bp.route('/privacy')
def privacy():
    """Stránka s ochranou soukromí."""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Stránka s podmínkami použití."""
    return render_template('terms.html')
