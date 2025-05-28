"""
Blueprint pro vzdělávací sekci aplikace.

Tento modul obsahuje routy pro vzdělávací sekci aplikace.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

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

@education_bp.route('/quiz/submit', methods=['POST'])
def quiz_submit():
    """Zpracování odpovědí z kvízu."""
    # Získání odpovědí z formuláře
    answers = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            answers[question_id] = value
    
    # Správné odpovědi (v reálné aplikaci by byly v databázi)
    correct_answers = {
        '1': 'b',
        '2': 'c',
        '3': 'a',
        '4': 'd',
        '5': 'b',
        '6': 'a',
        '7': 'c',
        '8': 'b',
        '9': 'd',
        '10': 'a'
    }
    
    # Vyhodnocení odpovědí
    score = 0
    results = {}
    for question_id, answer in answers.items():
        if question_id in correct_answers and answer == correct_answers[question_id]:
            score += 1
            results[question_id] = True
        else:
            results[question_id] = False
    
    # Výpočet procentuální úspěšnosti
    percentage = (score / len(correct_answers)) * 100
    
    # Přidání odznaku, pokud je uživatel přihlášen a dosáhl dobrého výsledku
    if session.get('user_id') and percentage >= 70:
        # V reálné aplikaci by zde byla logika pro přidání odznaku
        pass
    
    # Zobrazení výsledků
    return render_template('education/quiz_results.html', 
                          score=score, 
                          total=len(correct_answers), 
                          percentage=percentage, 
                          results=results)

@education_bp.route('/examples')
def examples():
    """Stránka s příklady dezinformací."""
    return render_template('education/examples.html')

@education_bp.route('/glossary')
def glossary():
    """Slovník pojmů."""
    return render_template('education/glossary.html')

@education_bp.route('/resources')
def resources():
    """Stránka s dalšími zdroji."""
    return render_template('education/resources.html')
