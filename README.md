# Návod k použití aplikace FactCheck

## Úvod

FactCheck je webová aplikace pro ověřování faktů pomocí umělé inteligence. Aplikace umožňuje uživatelům zadávat tvrzení, která jsou následně analyzována pomocí OpenAI API. Výsledkem analýzy je verdikt o pravdivosti tvrzení, vysvětlení a identifikace případných logických chyb nebo manipulativních technik.

## Instalace

### Požadavky
- Python 3.8 nebo vyšší
- Pip (správce balíčků pro Python)
- OpenAI API klíč

### Postup instalace

1. **Klonování repozitáře**
   ```
   git clone https://github.com/vas-username/factcheck.git
   cd factcheck
   ```

2. **Vytvoření virtuálního prostředí**
   ```
   python -m venv venv
   ```

3. **Aktivace virtuálního prostředí**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Instalace závislostí**
   ```
   pip install -r requirements.txt
   ```

5. **Nastavení OpenAI API klíče**
   
   Vytvořte soubor `.env` v kořenovém adresáři projektu a přidejte do něj váš OpenAI API klíč:
   ```
   OPENAI_API_KEY=vas-openai-api-klic
   ```

## Spuštění aplikace

1. **Lokální spuštění**
   ```
   python app.py
   ```
   Aplikace bude dostupná na adrese `http://localhost:5000`.

2. **Nasazení na produkční server**
   
   Aplikace je připravena pro nasazení na služby jako Heroku, Render nebo Vercel. Stačí nahrát kód do repozitáře na GitHubu a propojit ho s vybranou službou.

## Použití aplikace

### Ověření tvrzení

1. Na hlavní stránce klikněte na tlačítko "Ověřit tvrzení" nebo přejděte na záložku "Ověřit tvrzení" v navigačním menu.
2. Do textového pole zadejte tvrzení, které chcete ověřit.
3. Vyberte typ analýzy (rychlá, standardní, detailní).
4. Klikněte na tlačítko "Ověřit tvrzení".
5. Počkejte na výsledek analýzy, který se zobrazí na nové stránce.

### Vzdělávací sekce

V sekci "Vzdělávání" najdete materiály o mediální gramotnosti, dezinformacích, logických chybách a manipulativních technikách. Můžete si také vyzkoušet kvíz, který prověří vaše znalosti.

### Podpora projektu

Pokud chcete podpořit projekt, můžete se stát podporovatelem v sekci "Podpořit". K dispozici jsou různé úrovně podpory (bronzová, stříbrná, zlatá) s různými výhodami.

## Struktura projektu

```
factcheck/
├── app.py                  # Hlavní soubor aplikace
├── config.py               # Konfigurační soubor
├── models.py               # Databázové modely
├── services.py             # Služby (OpenAI API)
├── routes/                 # Routy aplikace
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── factcheck.py
│   ├── support.py
│   └── education.py
├── static/                 # Statické soubory
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # Šablony
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── errors/
│   ├── factcheck/
│   ├── education/
│   └── support/
└── requirements.txt        # Seznam závislostí
```

## Přizpůsobení aplikace

### Změna vzhledu

Vzhled aplikace můžete upravit v souborech CSS v adresáři `static/css/`. Hlavní soubor se styly je `main.css`.

### Přidání nových funkcí

Pro přidání nových funkcí můžete vytvořit nové routy v adresáři `routes/` a odpovídající šablony v adresáři `templates/`.

### Změna konfigurace

Konfigurační parametry aplikace najdete v souboru `config.py`. Zde můžete upravit nastavení OpenAI API, typy analýz a další parametry.

## Licence

Tento projekt je licencován pod MIT licencí. Podrobnosti najdete v souboru LICENSE.

## Kontakt

V případě dotazů nebo problémů nás kontaktujte na adrese info@factcheck.cz.
