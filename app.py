import os
import tempfile
from flask import Flask, render_template, request, jsonify
import openai
from PIL import Image
import base64
import io

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import imghdr


# Načti klíč z proměnné prostředí
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(_mname__)


def image_to_base64(image_file):
"""Převede obrázek na base64 řetězec (PNG)."""
img = Image.open(image_file)
buffered = io.BytesIO()
img.save(buffered, format="PNG")
return base64.b64encode(buffered.getvalue()).decode()

@app.route("/", methods=["GET"])
def index():
return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
if "image" not in request.files:
return jsonify({"error": "Žádný soubor nebyl odeslán"}), 400

image_file = request.files['image']
img_bytes = image_file.read()
# Limit velikosti 5 MB
if len(img_bytes) > 5 * 1024 * 1024:
return jsonify({"error": "Soubor je příliš velký (max 5 MB)."}), 400

b64_image = base64.b64encode(img_bytes).decode()



# Vytvoření promptu

user_prompt = """
Na vloženém obrázku je politik a jeho tweet. 
Vytěž z něj hlavní tvrzení, ověř jeho pravdivost a uveď rating (True/Partially True/False). 
Uveď také 1–2 stručné zdroje (např. odkaz na článek nebo oficiální statistiku). 
Shrň výsledek maximálně ve 3 větách, piš česky a srozumitelně.
""""""y:
response = openai.chat.completions.create(
model="gpt-4o-mini",
messages=[
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{b64_image}"
            },
            {
                "type": "text",
                "text": user_prompt
            }
        ],
    }
]
)


answer = response.choices[0].message.content
return jsonify({"analysis": answer})

except Exception as e:
return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
# Pro lokální vývoj; v produkci použijte WSGI server (gunicorn/uvicorn)
app.run(debug=True, host="0.0.0.0", port=5000)
