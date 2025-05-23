import os
import io
import base64
import logging
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image
import openai

# ---------- konfigurace logování ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- OpenAI ----------
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY není nastaven – /analyze selže při volání API.")

# ---------- Flask ----------
app = Flask(__name__)

# ---------- rate-limit ----------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"]   # globálně
)
limiter.init_app(app)

# ---------- pomocné funkce ----------
def image_to_base64(file_storage) -> str:
    """Převede obrázek na base64-encoded PNG řetězec."""
    try:
        img = Image.open(file_storage)
    except Exception as err:
        raise ValueError("Nepodařilo se otevřít obrázek.") from err

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ---------- routy ----------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
@limiter.limit("5 per minute")
def analyze():
    if "image" not in request.files:
        return jsonify(error="Žádný soubor nebyl odeslán."), 400

    image_file = request.files["image"]

    # limit 5 MB
    image_file.seek(0, os.SEEK_END)
    if image_file.tell() > 5 * 1024 * 1024:
        return jsonify(error="Soubor je příliš velký (max 5 MB)."), 400
    image_file.seek(0)

    try:
        b64_image = image_to_base64(image_file)

        user_prompt = (
            "Na vloženém obrázku je politik a jeho tweet. "
            "Vytěž z něj hlavní tvrzení, ověř jeho pravdivost a uveď rating "
            "(True/Partially True/False). "
            "Uveď také 1–2 stručné zdroje (např. odkaz na článek nebo oficiální statistiku). "
            "Shrň výsledek maximálně ve 3 větách. Piš česky a srozumitelně."
        )

        # ⬇️  Hlavní oprava – image_url MUSÍ být objekt s klíčem 'url'
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}"
                                # volitelně: "detail": "auto"
                            },
                        },
                        {
                            "type": "text",
                            "text": user_prompt,
                        },
                    ],
                }
            ],
        )

        answer = response.choices[0].message.content
        return jsonify(analysis=answer)

    except Exception as e:
        logger.exception("Chyba při analýze obrázku")
        return jsonify(error=str(e)), 500


# ---------- start aplikace ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render nastaví PORT
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
