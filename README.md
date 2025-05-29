# Dokumentace k aplikaci FactCheck s GPT-4o

## Přehled

Tato aplikace je nástroj pro ověřování faktů pomocí umělé inteligence, který využívá model GPT-4o od OpenAI. Aplikace umožňuje uživatelům zadávat tvrzení, která jsou následně analyzována a vyhodnocena z hlediska pravdivosti.

## Klíčové funkce

- Analýza tvrzení pomocí modelu GPT-4o
- Tři úrovně analýzy (rychlá, standardní, detailní)
- Identifikace logických chyb a manipulativních technik
- Uživatelské účty a historie analýz
- Vzdělávací materiály o fact-checkingu
- Systém podpory projektu

## Technické specifikace

- Backend: Flask (Python)
- Databáze: SQLAlchemy s SQLite (možnost přechodu na MySQL)
- Frontend: HTML, CSS, JavaScript
- API: OpenAI API (model GPT-4o)

## Struktura projektu

```
politweet-assistant-gpt4o/
├── app.py                 # Hlavní vstupní bod aplikace
├── config.py              # Konfigurační soubor
├── models.py              # Databázové modely
├── services.py            # Služby pro komunikaci s API
├── render.yaml            # Konfigurační soubor pro Render.com
├── requirements.txt       # Seznam závislostí
├── routes/                # Routy aplikace
│   ├── __init__.py
│   ├── auth.py            # Autentizace uživatelů
│   ├── education.py       # Vzdělávací obsah
│   ├── factcheck.py       # Ověřování faktů
│   ├── main.py            # Hlavní stránky
│   └── support.py         # Podpora projektu
├── static/                # Statické soubory
│   ├── css/
│   │   └── main.css       # Hlavní CSS soubor
│   ├── js/
│   │   └── main.js        # Hlavní JavaScript soubor
│   └── images/            # Obrázky
│       ├── logo.svg
│       └── hero-illustration.svg
└── templates/             # Šablony
    ├── base.html          # Základní šablona
    ├── index.html         # Hlavní stránka
    └── factcheck/         # Šablony pro ověřování faktů
        ├── index.html     # Formulář pro zadání tvrzení
        └── result.html    # Výsledek analýzy
```

## Instalace a spuštění

1. Naklonujte repozitář
2. Vytvořte virtuální prostředí: `python -m venv venv`
3. Aktivujte virtuální prostředí:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Nainstalujte závislosti: `pip install -r requirements.txt`
5. Nastavte proměnné prostředí:
   - `OPENAI_API_KEY` - váš API klíč pro OpenAI
   - `SECRET_KEY` - tajný klíč pro Flask (pro vývoj lze ponechat výchozí)
   - `DEBUG` - `True` pro vývoj, `False` pro produkci
6. Spusťte aplikaci: `python app.py`

## Nasazení na Render.com

1. Nahrajte kód do GitHub repozitáře
2. V Render dashboardu vyberte "New Web Service"
3. Zvolte "Build and deploy from a Git repository"
4. Vyberte váš GitHub repozitář
5. Render automaticky detekuje konfiguraci z `render.yaml`
6. **Důležité**: Nastavte proměnnou prostředí `OPENAI_API_KEY` s vaším API klíčem
7. Klikněte na "Create Web Service"

## Provedené opravy

1. **Oprava komunikace s OpenAI API**
   - Použití modelu GPT-4o místo GPT-4
   - Robustní zpracování odpovědí a ošetření chyb
   - Podrobné logování pro snadnější diagnostiku

2. **Oprava inicializace SQLAlchemy**
   - Zajištění jediné instance SQLAlchemy v celé aplikaci
   - Správná inicializace databáze v `app.py`
   - Robustní zpracování dat v metodě `from_openai_response`

3. **Vylepšení správy proměnných prostředí**
   - Přidána kontrola existence API klíče OpenAI
   - Přidáno varování při chybějícím API klíči
   - Vylepšena dokumentace kódu

4. **Aktualizace konfigurace Render.com**
   - Přidána definice proměnných prostředí
   - Nastaveno, aby OPENAI_API_KEY byl zadán manuálně (sync: false)
   - Přidáno automatické generování SECRET_KEY
   - Nastaveno DEBUG na false pro produkční prostředí

## Doporučení pro další vývoj

- Implementace monitoringu pro sledování využití API
- Přidání více modelů pro analýzu (např. možnost volby mezi GPT-4o a GPT-3.5-turbo)
- Rozšíření vzdělávacích materiálů
- Implementace exportu do PDF a DOCX
- Přidání více jazykových verzí
