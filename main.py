import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, request, jsonify, url_for
import os
import base64
from io import BytesIO
from PIL import Image
import time
import json
import openai
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Nastavení logování
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

# Konfigurace loggeru
logger = logging.getLogger('politweet_assistant')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler pro konzoli
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Handler pro soubor s rotací (max 5MB, max 5 souborů)
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Inicializace Flask aplikace
app = Flask(__name__)

# Nastavení rate limiteru
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Funkce pro načtení OpenAI API klíče
def load_api_key():
    # Nejprve zkusíme načíst z proměnné prostředí
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Pokud není v proměnné prostředí, zkusíme načíst z konfiguračního souboru
    if not api_key:
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('openai_api_key')
                    if api_key:
                        logger.info("OpenAI API klíč načten z konfiguračního souboru")
            except Exception as e:
                logger.error(f"Chyba při načítání konfiguračního souboru: {str(e)}")
    
    return api_key

# Nastavení OpenAI API klíče
openai.api_key = load_api_key()
if not openai.api_key:
    logger.error("VAROVÁNÍ: OPENAI_API_KEY není nastaven. API volání nebudou fungovat.")
    print("VAROVÁNÍ: OPENAI_API_KEY není nastaven. API volání nebudou fungovat.")
    print("Pro nastavení API klíče použijte proměnnou prostředí OPENAI_API_KEY nebo vytvořte soubor config.json")
    print("Příklad config.json: {\"openai_api_key\": \"váš-api-klíč\"}")

# Třída pro vlastní výjimky
class AnalysisError(Exception):
    """Základní třída pro výjimky při analýze obsahu"""
    pass

class APIKeyError(AnalysisError):
    """Výjimka pro chybějící nebo neplatný API klíč"""
    pass

class InputError(AnalysisError):
    """Výjimka pro neplatný vstup"""
    pass

class ImageProcessingError(AnalysisError):
    """Výjimka pro chyby při zpracování obrázku"""
    pass

class APIRequestError(AnalysisError):
    """Výjimka pro chyby při komunikaci s API"""
    pass

class APIRateLimitError(APIRequestError):
    """Výjimka pro překročení limitů API"""
    pass

# Funkce pro analýzu obsahu pomocí OpenAI API
def analyze_content(text=None, image=None, generate_social=False):
    """
    Analyzuje text nebo obrázek pomocí OpenAI API a vrací výsledek analýzy.
    
    Args:
        text (str, optional): Text k analýze. Výchozí hodnota je None.
        image (PIL.Image, optional): Obrázek k analýze. Výchozí hodnota je None.
        generate_social (bool, optional): Zda generovat odpověď pro sociální sítě. Výchozí hodnota je False.
    
    Returns:
        dict: Výsledek analýzy obsahující klíč "analysis" a případně "social".
        
    Raises:
        APIKeyError: Pokud není nastaven API klíč.
        InputError: Pokud není poskytnut text ani obrázek.
        ImageProcessingError: Pokud dojde k chybě při zpracování obrázku.
        APIRequestError: Pokud dojde k chybě při komunikaci s API.
        APIRateLimitError: Pokud dojde k překročení limitů API.
        AnalysisError: Pro ostatní chyby při analýze.
    """
    # Kontrola API klíče
    if not openai.api_key:
        logger.error("Chybí OpenAI API klíč")
        raise APIKeyError("OpenAI API klíč není nastaven. Nastavte jej pomocí proměnné prostředí OPENAI_API_KEY nebo v souboru config.json.")
    
    # Kontrola, zda byl poskytnut alespoň jeden vstup
    if not text and not image:
        logger.error("Nebyl poskytnut žádný vstup (text ani obrázek)")
        raise InputError("Musí být poskytnut text nebo obrázek k analýze")
    
    try:
        logger.info("Začátek analýzy obsahu")
        messages = []
        
        # Základní systémový prompt
        system_prompt = """Jsi expertní fact-checker, který analyzuje tvrzení v textech a obrázcích. Tvým úkolem je:

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
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Přidání uživatelského vstupu
        user_content = []
        
        if text:
            user_content.append({"type": "text", "text": text})
        
        if image:
            try:
                logger.info("Zpracování obrázku")
                
                # Omezení velikosti obrázku
                max_size = (1024, 1024)  # Maximální rozměry
                if image.width > max_size[0] or image.height > max_size[1]:
                    image.thumbnail(max_size, Image.LANCZOS)
                    logger.info(f"Obrázek zmenšen na {image.width}x{image.height}")
                
                # Konverze do RGB, pokud je to potřeba (např. pro RGBA nebo CMYK obrázky)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                    logger.info(f"Obrázek převeden do RGB z {image.mode}")
                
                # Převod obrázku na base64 s optimalizovanou kvalitou
                buffered = BytesIO()
                image.save(buffered, format="JPEG", quality=85, optimize=True)
                img_size = buffered.tell()
                logger.info(f"Velikost obrázku po kompresi: {img_size} bajtů")
                
                # Pokud je obrázek stále příliš velký, snížit kvalitu
                if img_size > 1000000:  # 1MB limit
                    quality = 70
                    buffered = BytesIO()
                    image.save(buffered, format="JPEG", quality=quality, optimize=True)
                    img_size = buffered.tell()
                    logger.info(f"Obrázek překomprimován s kvalitou {quality}, nová velikost: {img_size} bajtů")
                    
                    # Pokud je stále příliš velký, zkusit ještě nižší kvalitu
                    if img_size > 1000000:
                        quality = 50
                        buffered = BytesIO()
                        image.save(buffered, format="JPEG", quality=quality, optimize=True)
                        logger.info(f"Obrázek překomprimován s kvalitou {quality}")
                
                buffered.seek(0)
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_str}"
                    }
                })
                logger.info("Obrázek úspěšně zpracován")
            except Exception as e:
                logger.error(f"Chyba při zpracování obrázku: {str(e)}")
                raise ImageProcessingError(f"Chyba při zpracování obrázku: {str(e)}")
        
        messages.append({"role": "user", "content": user_content})
        
        # Volání OpenAI API
        logger.info("Volání OpenAI API pro analýzu obsahu")
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.2,
                max_tokens=5000
            )
            logger.info("Úspěšné volání OpenAI API")
        except openai.RateLimitError as e:
            logger.error(f"Překročení limitů OpenAI API: {str(e)}")
            raise APIRateLimitError(f"Překročení limitů OpenAI API: {str(e)}")
        except openai.AuthenticationError as e:
            logger.error(f"Chyba autentizace OpenAI API: {str(e)}")
            raise APIKeyError(f"Neplatný OpenAI API klíč: {str(e)}")
        except openai.APIError as e:
            logger.error(f"Chyba OpenAI API: {str(e)}")
            raise APIRequestError(f"Chyba při komunikaci s OpenAI API: {str(e)}")
        except Exception as e:
            logger.error(f"Neočekávaná chyba při volání OpenAI API: {str(e)}")
            raise AnalysisError(f"Neočekávaná chyba při analýze obsahu: {str(e)}")
        
        result = {
            "analysis": response.choices[0].message.content
        }
        
        # Pokud je požadována odpověď pro sociální sítě
        if generate_social:
            logger.info("Generování odpovědi pro sociální sítě")
            social_prompt = f"""Na základě této analýzy vytvoř krátkou odpověď pro sociální sítě (max 280 znaků),
která shrne hlavní zjištění. Začni s označením OVĚŘENO a příslušným emoji (✓, ❓, ✗) podle hodnocení.

Analýza:
{response.choices[0].message.content}"""
            
            try:
                social_response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Jsi stručný a výstižný fact-checker pro sociální sítě."},
                        {"role": "user", "content": social_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                result["social"] = social_response.choices[0].message.content
                logger.info("Úspěšně vygenerována odpověď pro sociální sítě")
            except Exception as e:
                logger.warning(f"Chyba při generování odpovědi pro sociální sítě: {str(e)}")
                result["social"] = "OVĚŘENO ❓ Došlo k chybě při generování odpovědi pro sociální sítě. #FactCheck"
        
        logger.info("Analýza obsahu úspěšně dokončena")
        return result
    
    except APIKeyError as e:
        logger.error(f"Chyba API klíče: {str(e)}")
        print(f"Chyba API klíče: {str(e)}")
        result = {
            "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nOmlouváme se, ale došlo k chybě s API klíčem. Zkontrolujte, zda je správně nastaven OPENAI_API_KEY v proměnné prostředí nebo v konfiguračním souboru config.json."
        }
        if generate_social:
            result["social"] = "OVĚŘENO ❓ Došlo k chybě s API klíčem. Zkontrolujte nastavení. #FactCheck"
        return result
    
    except InputError as e:
        logger.error(f"Chyba vstupu: {str(e)}")
        print(f"Chyba vstupu: {str(e)}")
        result = {
            "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nOmlouváme se, ale nebyl poskytnut žádný text ani obrázek k analýze."
        }
        if generate_social:
            result["social"] = "OVĚŘENO ❓ Nebyl poskytnut žádný obsah k analýze. #FactCheck"
        return result
    
    except ImageProcessingError as e:
        logger.error(f"Chyba zpracování obrázku: {str(e)}")
        print(f"Chyba zpracování obrázku: {str(e)}")
        result = {
            "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nOmlouváme se, ale došlo k chybě při zpracování obrázku. Zkuste jiný formát nebo menší velikost."
        }
        if generate_social:
            result["social"] = "OVĚŘENO ❓ Došlo k chybě při zpracování obrázku. Zkuste jiný formát. #FactCheck"
        return result
    
    except APIRateLimitError as e:
        logger.error(f"Překročení limitů API: {str(e)}")
        print(f"Překročení limitů API: {str(e)}")
        result = {
            "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nOmlouváme se, ale došlo k překročení limitů API. Zkuste to prosím později."
        }
        if generate_social:
            result["social"] = "OVĚŘENO ❓ Došlo k překročení limitů API. Zkuste to později. #FactCheck"
        return result
    
    except APIRequestError as e:
        logger.error(f"Chyba API požadavku: {str(e)}")
        print(f"Chyba API požadavku: {str(e)}")
        result = {
            "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nOmlouváme se, ale došlo k chybě při komunikaci s API. Zkuste to prosím znovu později."
        }
        if generate_social:
            result["social"] = "OVĚŘENO ❓ Došlo k chybě při komunikaci s API. Zkuste to znovu později. #FactCheck"
        return result
    
    except Exception as e:
        logger.error(f"Neočekávaná chyba při analýze obsahu: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"Neočekávaná chyba při analýze obsahu: {str(e)}")
        result = {
            "analysis": "Status: 3. Zavádějící\n\nVysvětlení:\nOmlouváme se, ale došlo k neočekávané chybě při analýze obsahu."
        }
        if generate_social:
            result["social"] = "OVĚŘENO ❓ Došlo k chybě při analyze. Zkuste to prosím znovu později. #FactCheck"
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
    """
    API endpoint pro analýzu obsahu.
    
    Očekává:
    - text: Text k analýze (volitelné)
    - image: Obrázek k analýze (volitelné)
    - generate_social: Zda generovat odpověď pro sociální sítě (volitelné)
    
    Vrací:
    - JSON s výsledkem analýzy
    """
    try:
        logger.info("Přijat požadavek na analýzu")
        
        # Získání parametrů z požadavku
        text = request.form.get('text', '')
        image_file = request.files.get('image')
        generate_social = request.form.get('generate_social') == 'true'
        
        # Inicializace proměnné pro obrázek
        image = None
        
        # Zpracování obrázku, pokud byl poskytnut
        if image_file:
            try:
                logger.info(f"Přijat obrázek: {image_file.filename}")
                image = Image.open(image_file.stream)
            except Exception as e:
                logger.error(f"Chyba při otevírání obrázku: {str(e)}")
                return jsonify({"error": "Chyba při zpracování obrázku"}), 400
        
        # Kontrola, zda byl poskytnut alespoň jeden vstup
        if not text and not image:
            logger.warning("Nebyl poskytnut žádný vstup (text ani obrázek)")
            return jsonify({"error": "Musí být poskytnut text nebo obrázek"}), 400
        
        # Analýza obsahu
        try:
            logger.info("Spouštím analýzu obsahu")
            result = analyze_content(text, image, generate_social)
            logger.info("Analýza obsahu dokončena")
            return jsonify(result)
        except Exception as e:
            logger.error(f"Chyba při analýze obsahu: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": f"Chyba při analýze obsahu: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Neočekávaná chyba v API endpointu: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Neočekávaná chyba: {str(e)}"}), 500

# Přidání informační stránky o API klíči
@app.route('/api-key-info')
def api_key_info():
    has_api_key = bool(openai.api_key)
    return render_template('api_key_info.html', has_api_key=has_api_key)

# Spuštění aplikace
if __name__ == "__main__":
    logger.info("Spouštění aplikace")
    app.run(debug=True, host='0.0.0.0')
