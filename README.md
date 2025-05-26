# Factchecker Asistent

Aplikace pro ověřování faktů v textech a obrázcích pomocí umělé inteligence (OpenAI GPT-4o).

## Popis projektu

Factchecker Asistent je webová aplikace vytvořená v Pythonu s využitím frameworku Flask, která umožňuje uživatelům ověřovat fakta v textech a obrázcích. Aplikace využívá OpenAI API (model GPT-4o) pro analýzu obsahu a poskytuje detailní hodnocení pravdivosti na pětistupňové škále.

## Funkce

- Analýza textů a ověřování faktů
- Analýza obrázků a jejich obsahu
- Hodnocení pravdivosti na pětistupňové škále
- Detailní vysvětlení s kontextem a zdroji
- Generování stručných odpovědí pro sociální sítě
- Responzivní design pro mobilní i desktopová zařízení

## Struktura projektu

- `main.py` - Hlavní soubor s Flask aplikací a logikou pro analýzu obsahu
- `requirements.txt` - Seznam závislostí
- `static/` - Složka se statickými soubory (CSS, JavaScript)
  - `css/` - CSS styly pro aplikaci
  - `js/` - JavaScript soubory pro frontend
- `templates/` - Složka s HTML šablonami
  - `base.html` - Základní šablona s hlavičkou a patičkou
  - `index.html` - Hlavní stránka s formulářem pro analýzu
  - `prompt.html` - Stránka s ukázkou promptu pro analýzu
  - `support.html` - Stránka s informacemi o podpoře projektu
- `logs/` - Složka pro logování aplikace

## Instalace a spuštění

### Požadavky

- Python 3.8 nebo novější
- Pip (správce balíčků pro Python)
- OpenAI API klíč

### Postup instalace

1. Naklonujte repozitář:
   ```
   git clone https://github.com/JiriMynar/politweet-assistant.git
   cd politweet-assistant
   ```

2. Vytvořte a aktivujte virtuální prostředí (doporučeno):
   ```
   python -m venv venv
   source venv/bin/activate  # Pro Linux/Mac
   venv\Scripts\activate     # Pro Windows
   ```

3. Nainstalujte závislosti:
   ```
   pip install -r requirements.txt
   ```

4. Nastavte OpenAI API klíč jako proměnnou prostředí:
   ```
   export OPENAI_API_KEY=váš_api_klíč  # Pro Linux/Mac
   set OPENAI_API_KEY=váš_api_klíč     # Pro Windows
   ```

### Spuštění aplikace

1. Spusťte aplikaci:
   ```
   python main.py
   ```

2. Otevřete webový prohlížeč a přejděte na adresu:
   ```
   http://localhost:5000
   ```

## Použití

1. Na hlavní stránce můžete:
   - Vložit text k analýze
   - Nahrát obrázek k analýze
   - Zaškrtnout možnost generování odpovědi pro sociální sítě

2. Klikněte na tlačítko "Ověřit fakta" pro spuštění analýzy

3. Výsledek analýzy se zobrazí pod formulářem a bude obsahovat:
   - Hodnocení pravdivosti
   - Detailní vysvětlení
   - Seznam zdrojů
   - Případně odpověď pro sociální sítě

## Licence

Tento projekt je licencován pod [MIT licencí](LICENSE).

## Autor

[JiriMynar](https://github.com/JiriMynar)

## Plánovaná vylepšení

V budoucích verzích plánujeme implementovat:

- Historii analýz a ukládání výsledků
- Rozšířené možnosti analýzy
- Integrované vyhledávání zdrojů
- Komunitní funkce a zpětnou vazbu
- Personalizaci a nastavení
- API pro integraci s jinými platformami
