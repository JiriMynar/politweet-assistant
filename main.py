"""
Factchecker Assistant – hlavní spouštěcí skript
----------------------------------------------
Vylepšená verze s robustnějším voláním OpenAI API a validací vstupů.

• Flask backend + Flask-Limiter pro základní rate-limit
• Oficiální klient `openai.OpenAI` (>= 1.3)
• Striktní kontrola proměnné **OPENAI_API_KEY** už při startu
• Validace velikosti, rozlišení a typu obrázku
• Přehledné JSON chyby + retry s exponenciálním čekáním

Před spuštěním:
    export OPENAI_API_KEY="…"
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
from openai._exceptions import (  # type: ignore
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# Konfigurace aplikace
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "webp"}
MAX_PIXEL_COUNT = 2048 * 2048  # doporučení OpenAI Vision
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB – hard limit OpenAI
OPENAI_TIMEOUT = 30  # sekund

# Kontrola API klíče hned při startu
if not (api_key := os.getenv("OPENAI_API_KEY")):
    raise RuntimeError("Environment variable OPENAI_API_KEY is not set – add it before running the app!")

client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.config.update(UPLOAD_FOLDER="uploads", MAX_CONTENT_LENGTH=MAX_FILE_SIZE_BYTES)

# Rate-limit – globálně 10/min, endpoint /analyze 5/min na IP
limiter = Limiter(get_remote_address, app=app, default_limits=["10/minute"])

# ---------------------------------------------------------------------------
# Pomocné funkce
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def image_to_data_url(image: Image.Image, fmt: str) -> str:
    """Převede PIL obrázek do base64 data-URL."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt.upper())
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/{fmt};base64,{encoded}"


def build_messages(prompt: str, img_data_url: str | None = None) -> List[Dict[str, Any]]:
    """Sestaví payload pro Chat Completion včetně (ne)povinného obrázku."""
    if img_data_url:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": img_data_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
    return [{"role": "user", "content": prompt}]


def chat_completion(messages: List[Dict[str, Any]], *, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
    """Volá OpenAI Chat Completion s retry mechanismem pro Rate Limit."""
    delay = 1.0  # první retry za 1 s, pak exponenciálně
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=OPENAI_TIMEOUT,
            )
            return response.choices[0].message.content  # type: ignore[attr-defined]
        except RateLimitError:
            if attempt == 4:
                raise  # už nezkoušet dál
            time.sleep(delay)
            delay *= 2
        except (APITimeoutError, BadRequestError, AuthenticationError):
            raise  # předáme dál do handleru
    raise RuntimeError("Unreachable retry loop – this should not happen")

# ---------------------------------------------------------------------------
# Routy
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/prompt")
def prompt_page():
    return render_template("prompt.html")


@app.route("/support")
def support_page():
    return render_template("support.html")


@app.route("/analyze", methods=["POST"])
@limiter.limit("5/minute")
def analyze():
    """Endpoint pro analýzu textu nebo obrázku."""
    # 1) JSON payload – text
    if request.is_json:
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return jsonify(error="'prompt' nesmí být prázdný."), 400
        messages = build_messages(prompt)
    # 2) Form-data s obrázkem (a volitelným textem)
    else:
        if "image" not in request.files:
            return jsonify(error="Chybí pole 'image'."), 400
        file = request.files["image"]
        prompt = (request.form.get("prompt") or "").strip() or "Analyzuj obrázek."
        if file.filename == "":
            return jsonify(error="Soubor nemá název."), 400
        if not allowed_file(file.filename):
            return jsonify(error="Nepodporovaný formát souboru."), 400
        # Kontrola velikosti (MAX_CONTENT_LENGTH) a rozlišení
        try:
            img = Image.open(file.stream)
        except Exception:
            return jsonify(error="Soubor není validní obrázek."), 400
        if img.width * img.height > MAX_PIXEL_COUNT:
            return jsonify(error="Obrázek je příliš velký; maximálně 2048×2048 px."), 400
        img_format = img.format.lower()
        img_data_url = image_to_data_url(img, img_format)
        messages = build_messages(prompt, img_data_url=img_data_url)

    # ------------------------------------------------------------------
    # Volání OpenAI API
    try:
        content = chat_completion(messages)
    except AuthenticationError:
        return jsonify(error="Serverová konfigurace: API klíč je neplatný."), 500
    except APITimeoutError:
        return jsonify(error="OpenAI API neodpovídá."), 504
    except BadRequestError as exc:
        return jsonify(error=f"Chybný požadavek: {exc}"), 400
    except RateLimitError:
        return jsonify(error="OpenAI API je momentálně přetížené, zkuste to za chvíli."), 429
    except Exception:
        return jsonify(error="Neočekávaná chyba na serveru."), 500

    return jsonify(result=content)

# ---------------------------------------------------------------------------
# Vstupní bod
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = bool(os.getenv("FLASK_DEBUG"))
    app.run(host="0.0.0.0", port=port, debug=debug)
