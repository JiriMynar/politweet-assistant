"""
Blueprint pro vzdělávací sekci aplikace.

Tento modul obsahuje routy pro vzdělávací materiály a mediální gramotnost.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models import db

education_bp = Blueprint('education', __name__)

@education_bp.route('/')
def index():
    """Hlavní stránka vzdělávací sekce."""
    return render_template('education/index.html')

@education_bp.route('/media-literacy')
def media_literacy():
    """Stránka o mediální gramotnosti."""
    return render_template('education/media_literacy.html')

@education_bp.route('/disinformation')
def disinformation():
    """Stránka o dezinformacích."""
    return render_template('education/disinformation.html')

@education_bp.route('/logical-fallacies')
def logical_fallacies():
    """Stránka o logických chybách."""
    return render_template('education/logical_fallacies.html')

@education_bp.route('/manipulation-techniques')
def manipulation_techniques():
    """Stránka o manipulativních technikách."""
    return render_template('education/manipulation_techniques.html')

@education_bp.route('/quiz')
def quiz():
    """Kvíz o mediální gramotnosti."""
    return render_template('education/quiz.html')

@education_bp.route('/examples')
def examples():
    """Příklady dezinformací a jejich analýzy."""
    return render_template('education/examples.html')

@education_bp.route('/resources')
def resources():
    """Zdroje pro další vzdělávání."""
    return render_template('education/resources.html')

@education_bp.route('/glossary')
def glossary():
    """Slovník pojmů."""
    return render_template('education/glossary.html')
