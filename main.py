import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, request, jsonify, url_for
import os
import base64
from io import BytesIO
from PIL import Image
import time
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Nastavení rate limiteru
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Simulace analýzy - v produkci by zde bylo volání OpenAI API
def analyze_content(text=None, image=None, generate_social=False):
    # Simulace zpoždění API
    time.sleep(1.5)
    
    # Ukázkový výsledek analýzy
    result = {
        "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nTvrzení obsahuje některé pravdivé informace, ale je prezentováno zavádějícím způsobem, který může vést k nesprávným závěrům. Zatímco uvedená statistika o 15% nárůstu je technicky správná, ignoruje důležitý kontext a dlouhodobé trendy.\n\nPodrobnější analýza ukazuje, že krátkodobý nárůst je součástí běžné sezónní fluktuace a při pohledu na pětileté období je celkový trend ve skutečnosti klesající o 8% ročně. Navíc, tvrzení nesprávně přisuzuje změnu konkrétní politice, ačkoliv odborné studie identifikovaly několik různých faktorů, které k této situaci přispívají.\n\nZdroje:\nhttps://www.statistickyurad.cz/analyzy/ekonomicke-trendy-2025\nhttps://www.ekonomicky-institut.cz/studie/faktory-rustu-2025\nhttps://www.univerzita.cz/vyzkum/analyza-dopadu-politik",
    }
    
    # Přidání odpovědi pro sociální sítě, pokud je požadována
    if generate_social:
        result["social"] = "OVĚŘENO ❓ Tvrzení o 15% nárůstu je ZAVÁDĚJÍCÍ. Ignoruje sezónní fluktuace a dlouhodobý klesající trend (-8% ročně). Více na factchecker-asistent.cz #FactCheck"
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prompt')
def prompt():
    # Ukázkový prompt pro šablonu
    analyze_prompt = """Jsi expertní fact-checker, který analyzuje tvrzení v textech a obrázcích. Tvým úkolem je:

1. Důkladně analyzovat předložené tvrzení nebo obrázek
2. Určit pravdivost na pětistupňové škále:
   1. Pravda - tvrzení je zcela pravdivé a úplné
   2. Spíše pravda - tvrzení je převážně pravdivé s drobnými nepřesnostmi
   3. Zavádějící - tvrzení obsahuje pravdivé prvky, ale je prezentováno zavádějícím způsobem
   4. Spíše lež - tvrzení je převážně nepravdivé, ale obsahuje některé pravdivé prvky
   5. Lež - tvrzení je zcela nepravdivé

3. Poskytnout podrobné vysvětlení na úrovni vysokoškoláka, které zahrnuje:
   - Kontext a souvislosti
   - Relevantní fakta a statistiky
   - Vysvětlení, proč je tvrzení pravdivé/nepravdivé/zavádějící
   - U částečně pravdivých tvrzení uvést, jak by mělo být správně formulováno

4. Uvést konkrétní, ověřitelné zdroje, které podporují tvé hodnocení
   - Preferovat primární zdroje (studie, oficiální statistiky, původní dokumenty)
   - Uvádět přímé odkazy na zdroje

Formát odpovědi:
Status: [číslo stupně. název stupně]

Vysvětlení:
[Podrobné vysvětlení]

Zdroje:
[Seznam zdrojů s odkazy]"""

    return render_template('prompt.html', ANALYZE_PROMPT=analyze_prompt)

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def api_analyze():
    text = request.form.get('text', '')
    image_file = request.files.get('image')
    generate_social = request.form.get('generate_social') == 'true'
    
    image = None
    if image_file:
        try:
            image = Image.open(image_file.stream)
            # V produkci by zde bylo zpracování obrázku pro OpenAI API
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    # Kontrola, zda byl poskytnut alespoň jeden vstup
    if not text and not image:
        return jsonify({"error": "Musí být poskytnut text nebo obrázek"}), 400
    
    try:
        result = analyze_content(text, image, generate_social)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
