from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI
from PIL import Image
import io
import base64

app = Flask(__name__)

client = OpenAI()

ANALYZE_PROMPT = (
    "Analyzuj předložené tvrzení (nebo informaci na obrázku) a ověř jeho pravdivost na základě dostupných faktických informací. "
    "Hodnoť výsledek na této pětistupňové škále:\n"
    "1. Pravda\n"
    "2. Spíše pravda\n"
    "3. Zavádějící\n"
    "4. Spíše lež\n"
    "5. Lež\n\n"
    "Uveď jasný status a detailně vysvětli své hodnocení (na úrovni vysokoškoláka, včetně souvislostí, relevantních dat a argumentace). "
    "Připoj také konkrétní ověřitelné zdroje (odkazy na články, studie, oficiální statistiky apod.), které své tvrzení podporují. "
    "Piš česky, přehledně a v několika odstavcích.\n\n"
    "Struktura odpovědi:\n"
    "Status: [zvol jeden z 5 stupňů]\n"
    "Vysvětlení: [podrobné odůvodnění]\n"
    "Zdroje: [seznam konkrétních odkazů]\n"
)

def analyze_with_gpt(text):
  response =   client.chat.completions.create
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ANALYZE_PROMPT},
            {"role": "user", "content": text}
        ],
        max_tokens=1000,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text", "").strip()
    image = request.files.get("image")

    if image and image.filename:
        img_bytes = image.read()
        base64_img = base64.b64encode(img_bytes).decode("utf-8")
        user_input = f"Na obrázku je následující obsah (base64 PNG): {base64_img}"
    elif text:
        user_input = text
    else:
        return jsonify({"error": "Musíš nahrát obrázek nebo zadat text!"}), 400

    try:
        result = analyze_with_gpt(user_input)
        return jsonify({"analysis": result})
    except Exception as e:
        return jsonify({"error": f"Nastala chyba: {str(e)}"}), 500

if __name__ == "__main__":
app.run(debug=False)
