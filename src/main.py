"""
Fact-Checking Application
-------------------------
Hlavní vstupní bod aplikace pro ověřování faktů a analýzu pravdivosti informací.
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import logging
import json
import uuid
from datetime import datetime

# Inicializace aplikace
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_development')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {
    'text': {'txt', 'md', 'pdf', 'docx', 'doc'},
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'},
    'video': {'mp4', 'mov', 'avi', 'webm'}
}

# Zajištění existence složky pro uploady
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Konfigurace logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import služeb pro analýzu (importy jsou zde, ale implementace bude v samostatných souborech)
try:
    from services.text_analyzer import TextAnalyzer
    from services.image_analyzer import ImageAnalyzer
    from services.audio_analyzer import AudioAnalyzer
    from services.video_analyzer import VideoAnalyzer
    from services.fact_checker import FactChecker
    services_loaded = True
except ImportError:
    logger.warning("Některé služby nebyly načteny. Aplikace bude fungovat v omezeném režimu.")
    services_loaded = False

# Pomocné funkce
def allowed_file(filename, file_type=None):
    """Kontrola, zda je soubor povoleného typu."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type:
        return ext in app.config['ALLOWED_EXTENSIONS'].get(file_type, set())
    
    # Kontrola pro všechny typy
    for allowed_exts in app.config['ALLOWED_EXTENSIONS'].values():
        if ext in allowed_exts:
            return True
    return False

def get_file_type(filename):
    """Určení typu souboru podle přípony."""
    if '.' not in filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in app.config['ALLOWED_EXTENSIONS'].items():
        if ext in extensions:
            return file_type
    return None

def generate_result_id():
    """Generování unikátního ID pro výsledek analýzy."""
    return str(uuid.uuid4())

# Simulace analýzy pro demonstrační účely
def simulate_analysis(content, expertise_level, analysis_length):
    """
    Simuluje analýzu obsahu pro demonstrační účely.
    V produkční verzi by tato funkce byla nahrazena skutečnou analýzou.
    """
    # Simulované výsledky analýzy
    truth_ratings = [
        "Pravdivé", "Převážně pravdivé", "Částečně pravdivé", 
        "Převážně nepravdivé", "Nepravdivé", "Zavádějící",
        "Nedostatečné údaje", "Neověřitelné", "Satira"
    ]
    
    # Pro demonstrační účely vracíme simulovaný výsledek
    import random
    
    # Simulace různé délky analýzy podle nastavení
    detail_multiplier = {
        "brief": 1,
        "standard": 2,
        "detailed": 3,
        "exhaustive": 4
    }.get(analysis_length, 2)
    
    # Simulace různé odbornosti podle nastavení
    expertise_terms = {
        "basic": ["jednoduchý", "základní", "běžný", "srozumitelný"],
        "medium": ["středně pokročilý", "odborný", "specializovaný", "technický"],
        "advanced": ["pokročilý", "vysoce odborný", "komplexní", "vědecký"],
        "expert": ["expertní", "vědecky přesný", "akademický", "vysoce specializovaný"]
    }.get(expertise_level, ["standardní"])
    
    # Generování simulovaného výsledku
    result = {
        "id": generate_result_id(),
        "timestamp": datetime.now().isoformat(),
        "content_summary": f"Analýza textu o délce přibližně {len(content)} znaků.",
        "truth_rating": random.choice(truth_ratings),
        "analysis": {
            "detailed_explanation": f"Toto je {''.join(random.sample(expertise_terms, 1))} rozbor poskytnutého obsahu. " + 
                                   f"Analýza je {'krátká' if detail_multiplier == 1 else 'středně dlouhá' if detail_multiplier == 2 else 'podrobná' if detail_multiplier == 3 else 'velmi podrobná'}. " +
                                   f"V reálné aplikaci by zde byla skutečná analýza obsahu s ověřením faktů.",
            "key_points": [
                "Toto je první klíčový bod analýzy.",
                "Druhý bod obsahuje další důležité informace.",
                "Třetí bod uzavírá základní analýzu."
            ] * detail_multiplier,
            "sources": [
                {"name": "Důvěryhodný zdroj 1", "url": "https://example.com/source1", "reliability": "Vysoká"},
                {"name": "Odborná publikace", "url": "https://example.com/source2", "reliability": "Velmi vysoká"},
                {"name": "Statistický úřad", "url": "https://example.com/source3", "reliability": "Oficiální"}
            ],
            "alternative_perspectives": [
                "První alternativní pohled na problematiku.",
                "Druhý pohled nabízí odlišnou interpretaci."
            ] if detail_multiplier > 1 else [],
            "suggested_responses": [
                "Informativní odpověď: Podle dostupných informací...",
                "Vzdělávací odpověď: Je důležité si uvědomit, že...",
                "Humorná odpověď: Kdyby fakta mohla mluvit, řekla by..."
            ]
        },
        "settings": {
            "expertise_level": expertise_level,
            "analysis_length": analysis_length
        }
    }
    
    return result

# Routy aplikace
@app.route('/')
def index():
    """Hlavní stránka aplikace."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Zpracování požadavku na analýzu."""
    # Kontrola, zda byl poskytnut nějaký obsah
    if 'text' not in request.form and 'file' not in request.files:
        flash('Nebyl poskytnut žádný obsah k analýze.', 'error')
        return redirect(url_for('index'))
    
    # Získání nastavení analýzy
    expertise_level = request.form.get('expertise_level', 'medium')
    analysis_length = request.form.get('analysis_length', 'standard')
    
    content = ""
    file_path = None
    file_type = None
    
    # Zpracování textového vstupu
    if 'text' in request.form and request.form['text'].strip():
        content = request.form['text'].strip()
        file_type = 'text'
    
    # Zpracování nahraného souboru
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash('Nebyl vybrán žádný soubor.', 'error')
            return redirect(url_for('index'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_type = get_file_type(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Pro textové soubory načteme obsah
            if file_type == 'text':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Pokud nejde o textový soubor v UTF-8, necháme ho zpracovat jako binární
                    content = f"Soubor: {filename}"
            else:
                content = f"Soubor: {filename} (typ: {file_type})"
        else:
            flash('Nepodporovaný typ souboru.', 'error')
            return redirect(url_for('index'))
    
    # Provedení analýzy (v této verzi simulované)
    try:
        if services_loaded and file_type:
            # Toto by v produkční verzi volalo skutečné analyzátory
            result = simulate_analysis(content, expertise_level, analysis_length)
        else:
            # Fallback na simulaci
            result = simulate_analysis(content, expertise_level, analysis_length)
        
        # Uložení výsledku pro pozdější zobrazení
        result_id = result['id']
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'results'), exist_ok=True)
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'results', f"{result_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Přesměrování na stránku s výsledky
        return redirect(url_for('results', result_id=result_id))
    
    except Exception as e:
        logger.error(f"Chyba při analýze: {str(e)}", exc_info=True)
        flash(f'Došlo k chybě při analýze: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results/<result_id>')
def results(result_id):
    """Zobrazení výsledků analýzy."""
    try:
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results', f"{result_id}.json")
        if not os.path.exists(result_path):
            flash('Požadovaný výsledek nebyl nalezen.', 'error')
            return redirect(url_for('index'))
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return render_template('results.html', result=result)
    
    except Exception as e:
        logger.error(f"Chyba při zobrazení výsledků: {str(e)}", exc_info=True)
        flash(f'Došlo k chybě při zobrazení výsledků: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint pro analýzu obsahu."""
    try:
        # Kontrola, zda byl poskytnut obsah
        if not request.json or ('text' not in request.json and 'file_url' not in request.json):
            return jsonify({
                'error': 'Nebyl poskytnut žádný obsah k analýze.'
            }), 400
        
        # Získání nastavení
        expertise_level = request.json.get('expertise_level', 'medium')
        analysis_length = request.json.get('analysis_length', 'standard')
        
        # Zpracování obsahu
        content = request.json.get('text', '')
        file_url = request.json.get('file_url', '')
        
        # Simulace analýzy
        result = simulate_analysis(content or file_url, expertise_level, analysis_length)
        
        # Uložení výsledku
        result_id = result['id']
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'results'), exist_ok=True)
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'results', f"{result_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Vrácení ID výsledku
        return jsonify({
            'result_id': result_id,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"API chyba: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/results/<result_id>', methods=['GET'])
def api_results(result_id):
    """API endpoint pro získání výsledků analýzy."""
    try:
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results', f"{result_id}.json")
        if not os.path.exists(result_path):
            return jsonify({
                'error': 'Požadovaný výsledek nebyl nalezen.'
            }), 404
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"API chyba při získání výsledků: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/download/<result_id>')
def download_results(result_id):
    """Stažení výsledků analýzy ve formátu PDF."""
    # Toto je zjednodušená implementace - v produkční verzi by generovala skutečné PDF
    try:
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results', f"{result_id}.json")
        if not os.path.exists(result_path):
            flash('Požadovaný výsledek nebyl nalezen.', 'error')
            return redirect(url_for('index'))
        
        # V produkční verzi by zde byl kód pro generování PDF
        # Pro demonstrační účely vracíme JSON soubor
        return send_file(
            result_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f"fact-check-result-{result_id}.json"
        )
    
    except Exception as e:
        logger.error(f"Chyba při stahování výsledků: {str(e)}", exc_info=True)
        flash(f'Došlo k chybě při stahování výsledků: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Obsluha chyby 404."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Obsluha chyby 500."""
    logger.error(f"Serverová chyba: {str(e)}", exc_info=True)
    return render_template('500.html'), 500

# Spuštění aplikace
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    # Informace o spuštění
    logger.info(f"Spouštění aplikace na portu {port}, debug={debug}")
    
    # Spuštění aplikace
    app.run(host='0.0.0.0', port=port, debug=debug)
