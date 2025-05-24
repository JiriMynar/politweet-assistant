import os
import io
import base64
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# rate-limit: max 10 požadavků za minutu z jedné IP
limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])

def image_to_base64(file_storage) -> str:
    """Převede obrázek (werkzeug FileStorage) na base64 PNG řetězec."""
    img = Image.open(file_storage)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
@limiter.limit("5/minute")
def analyze():
    if "image" not in request.files:
        return jsonify(error="Žádný soubor nebyl odeslán"), 400

    image_file = request.files["image"]

    # max 5 MB
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
            "Shrň výsledek maximálně ve 3 větách, piš česky a srozumitelně."
        )

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url",
                         "image_url": f"data:image/png;base64,{b64_image}"},
                        {"type": "text", "text": user_prompt},
                    ],
                }
            ],
        )
        answer = response.choices[0].message.content
        return jsonify(analysis=answer)

    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    # Pro lokální vývoj; v produkčním nasazení použijte WSGI (gunicorn/uvicorn)
    app.run(debug=True, host="0.0.0.0", port=5000)
