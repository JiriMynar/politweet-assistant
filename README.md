# Fact-Checking Aplikace

Webová aplikace pro ověřování faktů a analýzu pravdivosti informací z různých zdrojů.

## Popis

Tato aplikace umožňuje uživatelům nahrávat různé typy obsahu (text, obrázky, audio, video) a poskytuje detailní analýzu pravdivosti s různými úrovněmi podrobnosti a odbornosti. Aplikace je navržena jako nástroj pro boj proti dezinformacím a pomáhá uživatelům rozlišovat mezi pravdivými a nepravdivými informacemi.

## Funkce

- **Analýza různých typů médií**:
  - Textový obsah (přímý text, dokumenty)
  - Obrazový obsah (obrázky obsahující text, grafy, tabulky)
  - Audio obsah (přepisy nahrávek)
  - Video obsah (přepisy videí)

- **Škála hodnocení pravdivosti**:
  - Pravdivé
  - Převážně pravdivé
  - Částečně pravdivé
  - Převážně nepravdivé
  - Nepravdivé
  - Zavádějící
  - Nedostatečné údaje
  - Neověřitelné
  - Satira

- **Přizpůsobitelná analýza**:
  - Nastavení úrovně odbornosti (základní, střední, pokročilá, expertní)
  - Nastavení délky analýzy (stručná, standardní, podrobná, vyčerpávající)

- **Strukturovaný výstup**:
  - Souhrn analyzovaného obsahu
  - Celkové hodnocení pravdivosti
  - Detailní analýza jednotlivých tvrzení
  - Seznam zdrojů a referencí
  - Alternativní perspektivy
  - Navrhované reakce pro sdílení

- **Moderní uživatelské rozhraní**:
  - Responzivní design pro desktop, tablet i mobilní zařízení
  - Intuitivní ovládání s drag & drop funkcionalitou
  - Vizuální indikátory pravdivosti
  - Možnost exportu výsledků do PDF

## Technologie

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Databáze**: SQLite (vývojové prostředí), PostgreSQL (produkce)
- **Deployment**: Připraveno pro nasazení na Render.com

## Instalace a spuštění

### Požadavky

- Python 3.8+
- pip (správce balíčků pro Python)
- Virtuální prostředí (doporučeno)

### Lokální instalace

1. Naklonujte repozitář:
   ```
   git clone https://github.com/vas-username/fact-checking-app.git
   cd fact-checking-app
   ```

2. Vytvořte a aktivujte virtuální prostředí:
   ```
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```

3. Nainstalujte závislosti:
   ```
   pip install -r requirements.txt
   ```

4. Spusťte aplikaci:
   ```
   cd src
   python main.py
   ```

5. Otevřete prohlížeč a přejděte na adresu `http://localhost:5000`

### Nasazení na Render.com

1. Vytvořte účet na [Render.com](https://render.com/)

2. Klikněte na "New" a vyberte "Web Service"

3. Propojte svůj GitHub repozitář

4. Nastavte následující parametry:
   - **Name**: Zvolte název vaší aplikace
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src && gunicorn main:app`

5. Klikněte na "Create Web Service"

## Struktura projektu

```
fact-checking-app/
├── src/                      # Zdrojový kód aplikace
│   ├── main.py               # Hlavní vstupní bod aplikace
│   ├── models/               # Datové modely
│   ├── services/             # Služby pro zpracování dat
│   ├── utils/                # Pomocné nástroje
│   ├── static/               # Statické soubory (CSS, JS, obrázky)
│   ├── templates/            # HTML šablony
│   └── api/                  # API endpointy
├── tests/                    # Testy
├── requirements.txt          # Seznam závislostí
└── README.md                 # Dokumentace projektu
```

## API Dokumentace

### Hlavní endpointy

- `POST /api/analyze`: Nahrání obsahu k analýze
  ```json
  {
    "text": "Text k analýze",
    "expertise_level": "medium",
    "analysis_length": "standard"
  }
  ```

- `GET /api/results/<result_id>`: Získání výsledků analýzy

### Odpověď API

```json
{
  "id": "unique-result-id",
  "timestamp": "2023-08-15T14:30:00",
  "content_summary": "Analýza textu...",
  "truth_rating": "Částečně pravdivé",
  "analysis": {
    "detailed_explanation": "...",
    "key_points": ["...", "..."],
    "sources": [
      {"name": "Zdroj 1", "url": "https://example.com", "reliability": "Vysoká"}
    ],
    "alternative_perspectives": ["...", "..."],
    "suggested_responses": ["...", "..."]
  },
  "settings": {
    "expertise_level": "medium",
    "analysis_length": "standard"
  }
}
```

## Licence

Tento projekt je licencován pod [MIT licencí](LICENSE).

## Kontakt

Pro jakékoli dotazy nebo připomínky prosím vytvořte issue v tomto repozitáři nebo kontaktujte autora.
