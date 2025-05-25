# Factchecker Asistent

Aplikace pro ověřování faktů v textech a obrázcích pomocí umělé inteligence.

## Popis projektu

Factchecker Asistent je webová aplikace, která umožňuje uživatelům nahrát obrázek nebo vložit text a získat analýzu pravdivosti pomocí OpenAI API. Aplikace poskytuje hodnocení na pětistupňové škále (pravda, spíše pravda, zavádějící, spíše lež, lež), podrobné vysvětlení a odkazy na zdroje.

## Struktura projektu

```
factchecker-app/
├── main.py                # Hlavní vstupní bod aplikace
├── static/                # Statické soubory
│   └── css/
│       └── custom.css     # Vlastní CSS styly
└── templates/             # HTML šablony
    ├── base.html          # Základní šablona
    ├── index.html         # Hlavní stránka s fact-checkerem
    ├── prompt.html        # Stránka s popisem promptu
    └── support.html       # Stránka pro podporu projektu
```

## Instalace a spuštění

1. Klonování repozitáře:
```bash
git clone https://github.com/JiriMynar/factchecker-assistant.git
cd factchecker-assistant
```

2. Vytvoření a aktivace virtuálního prostředí:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instalace závislostí:
```bash
pip install -r requirements.txt
```

4. Nastavení API klíče:
```bash
export OPENAI_API_KEY="VÁŠ_API_KLÍČ"  # Windows: set OPENAI_API_KEY=VÁŠ_API_KLÍČ
```

5. Spuštění aplikace:
```bash
python main.py
```

Aplikace bude dostupná na adrese `http://localhost:5000`.

## Funkce

- Nahrávání obrázků pomocí drag & drop nebo Ctrl+V
- Analýza textu nebo obrázků pomocí OpenAI API
- Hodnocení pravdivosti na pětistupňové škále
- Detailní vysvětlení s odkazy na zdroje
- Generování odpovědí pro sociální sítě
- Responzivní design pro všechna zařízení

## Technologie

- **Backend**: Python s frameworkem Flask
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript (Alpine.js)
- **API**: OpenAI API (model GPT-4o)

## Nasazení do produkce

Pro produkční nasazení doporučujeme:
1. Použít WSGI server (např. Gunicorn)
2. Nastavit reverzní proxy (např. Nginx) s HTTPS
3. Zajistit bezpečné uložení API klíče v proměnných prostředí

Příklad spuštění s Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## Autor

Vytvořil [JiriMynar](https://github.com/JiriMynar)
