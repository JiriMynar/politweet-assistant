"""
Factchecker Assistant – hlavní spouštěcí skript
----------------------------------------------
Zjednodušená, ale stále robustní verze pro snadné nasazení.

• Flask backend + Flask-Limiter (rate-limit)
• Oficiální klient `openai.OpenAI` (>= 1.3)
• Kontrola proměnné **OPENAI_API_KEY** už při startu
• Validace velikosti, rozlišení a typu obrázku
• Přehledné JSON chyby + jednoduchý retry při přetížení API

Před spuštěním:
    export OPENAI_API_KEY="YOUR_KEY"
    pip install -r requirements.txt
"""
from __future__ import annotations

import base64
import io
import os
import time
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image

from openai import OpenAI
from openai._exceptions import (
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# Konfigurace
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_PIXEL_COUNT = 2048 * 2048          # max počet pixelů  (≈ 4 Mpx)
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024 # 20 MB – tvrdý limit OpenAI
OPENAI_TIMEOUT = 30                    # s

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Proměnná OPENAI_API_KEY není nastavena!")

client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.config.update(UPLOAD_FOLDER="uploads", MAX_CONTENT_LENGTH=MAX_FILE_SIZE_BYTES)

limiter = Limiter(get_remote_address, app=app, default_limits=["10/minute"])

# ---------------------------------------------------------------------------
# Pomocné funkce
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_data_url(image: Image.Image, fmt: str) -> str:
    """Převede PIL obrázek na base64 data-URL (nutné pro Vision model)."""
    buf = io.BytesIO()
    image.save(buf, format=fmt.upper())
    encoded = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/{fmt};base64,{encoded}"


def build_messages(prompt: str, img_data_url: str | None = None) -> List[Dict[str, Any]]:
    if img_data_url:
        return [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": img_data_url}},
                {"type": "text", "text": prompt},
            ],
        }]
    return [{"role": "user", "content": prompt}]


def chat_completion(messages: List[Dict[str, Any]], model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
    """Zavolá OpenAI Chat-Completion se 4 retenzními pokusy při 429."""
    delay = 1.0
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=OPENAI_TIMEOUT,
            )
            return resp.choices[0].message.content  # type: ignore[attr-defined]
        except RateLimitError:
            if attempt == 4:
                raise
            time.sleep(delay)
            delay *= 2
        except (APITimeoutError, BadRequestError, AuthenticationError):
            raise
    raise RuntimeError("Nepodařilo se zavolat OpenAI ani po opakováních.")

# ---------------------------------------------------------------------------
# Routy – URL adresy aplikace
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    # jednoduchá uvítací stránka (může být statická šablona)
    return render_template("index.html")


@app.route("/prompt", endpoint="prompt")
def prompt_view():
    return render_template("prompt.html")


@app.route("/support", endpoint="support")
def support_view():
    return render_template("support.html")


@app.route("/analyze", methods=["POST"])
@limiter.limit("5/minute")
def analyze():
    """Zpracuje buď textový prompt (JSON), nebo obrázek (form-data)."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return jsonify(error="'prompt' musí být vyplněn."), 400
        messages = build_messages(prompt)
    else:  # form-data
        if "image" not in request.files:
            return jsonify(error="Chybí pole 'image'."), 400
        file = request.files["image"]
        prompt = (request.form.get("prompt") or "Analyzuj obrázek.").strip()
        if not allowed_file(file.filename):
            return jsonify(error="Nepodporovaný typ souboru."), 400
        try:
            img = Image.open(file.stream)
        except Exception:
            return jsonify(error="Soubor není validní obrázek."), 400
        if img.width * img.height > MAX_PIXEL_COUNT:
            return jsonify(error="Obrázek přesahuje 2048×2048 px."), 400
        img_data_url = image_to_data_url(img, img.format.lower())
        messages = build_messages(prompt, img_data_url)

    # --- volání OpenAI ---
    try:
        content = chat_completion(messages)
    except AuthenticationError:
        return jsonify(error="Nesprávný OPENAI_API_KEY."), 500
    except APITimeoutError:
        return jsonify(error="OpenAI API neodpovídá."), 504
    except BadRequestError as exc:
        return jsonify(error=f"Chybný požadavek: {exc}"), 400
    except RateLimitError:
        return jsonify(error="OpenAI je přetížené, zkuste to za chvíli."), 429
    except Exception:
        return jsonify(error="Neočekávaná chyba na serveru."), 500

    return jsonify(result=content)

# ---------------------------------------------------------------------------
# Spuštění
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

