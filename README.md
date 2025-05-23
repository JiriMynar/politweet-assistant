# Politweet Asistent

Webová aplikace, která umožňuje nahrát obrázek (tweet politika) a získat stručnou, srozumitelnou analýzu pomocí OpenAI Vision.

## Požadavky

- Python 3.9+
- Účet a API klíč pro OpenAI (`OPENAI_API_KEY`)

## Instalace

```bash
git clone https://github.com/<VAŠE_UŽIVATELSKÉ_JMÉNO>/politweet-assistant.git
cd politweet-assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Spuštění

```bash
export OPENAI_API_KEY="VAŠE_API_KLÍČ"
python app.py
```

Aplikace poběží na `http://localhost:5000`.

## Struktura projektu

```
politweet-assistant/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    └── style.css
```

## Nasazení

Pro produkční provoz doporučujeme WSGI server (např. gunicorn) za reverzní proxy (nginx) s HTTPS.

---

Vytvořeno automaticky pomocí GitHub web‑editoru.
