# Návod k použití aplikace FactCheck

## Obsah
1. Úvod
2. Instalace
3. Konfigurace
4. Spuštění aplikace
5. Struktura projektu
6. Přizpůsobení a rozšíření
7. Nasazení do produkce
8. Kontakt a podpora

## 1. Úvod

FactCheck je webová aplikace pro ověřování faktů s využitím umělé inteligence (OpenAI API). Aplikace umožňuje uživatelům ověřovat tvrzení, učit se o mediální gramotnosti a podporovat projekt.

Hlavní funkce:
- Ověřování tvrzení pomocí OpenAI API
- Vzdělávací sekce o mediální gramotnosti
- Systém podpory projektu
- Uživatelské účty a správa profilu
- Responzivní design pro mobilní i desktopové zařízení

## 2. Instalace

### Požadavky
- Python 3.8 nebo novější
- pip (správce balíčků pro Python)
- MySQL databáze (volitelné, lze použít SQLite pro vývoj)
- OpenAI API klíč

### Postup instalace

1. Naklonujte repozitář z GitHubu:
```bash
git clone https://github.com/vas-username/factcheck.git
cd factcheck
```

2. Vytvořte a aktivujte virtuální prostředí:
```bash
python -m venv venv
source venv/bin/activate  # Na Windows: venv\Scripts\activate
```

3. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

## 3. Konfigurace

### OpenAI API klíč

Pro správnou funkci aplikace je nutné nastavit OpenAI API klíč. Můžete to udělat jedním z následujících způsobů:

1. Nastavením proměnné prostředí:
```bash
export OPENAI_API_KEY=vas-api-klic
```

2. Vytvořením souboru `.env` v kořenovém adresáři projektu:
```
OPENAI_API_KEY=vas-api-klic
SECRET_KEY=tajny-klic-pro-flask
```

### Konfigurace databáze

Ve výchozím nastavení aplikace používá SQLite databázi. Pro použití MySQL upravte konfiguraci v souboru `src/main.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'factcheck')}"
```

A nastavte příslušné proměnné prostředí:
```bash
export DB_USERNAME=vase_uzivatelske_jmeno
export DB_PASSWORD=vase_heslo
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=factcheck
```

## 4. Spuštění aplikace

### Vývojový server

Pro spuštění vývojového serveru použijte:
```bash
cd src
python main.py
```

Aplikace bude dostupná na adrese http://localhost:5000

### Inicializace databáze

Při prvním spuštění se automaticky vytvoří databázové tabulky. Pro naplnění databáze ukázkovými daty můžete použít skript:
```bash
python init_db.py
```

## 5. Struktura projektu

```
factcheck_app/
├── requirements.txt       # Seznam závislostí
├── src/                   # Zdrojový kód aplikace
│   ├── main.py            # Hlavní soubor aplikace
│   ├── models/            # Databázové modely
│   ├── routes/            # Routy aplikace
│   ├── services/          # Služby (OpenAI API, atd.)
│   ├── static/            # Statické soubory (CSS, JS, obrázky)
│   └── templates/         # HTML šablony
├── architecture.md        # Popis architektury aplikace
└── validation.md          # Validace požadavků
```

## 6. Přizpůsobení a rozšíření

### Úprava vzhledu

Pro úpravu vzhledu aplikace můžete upravit soubory:
- `src/static/css/main.css` - hlavní CSS soubor
- `src/static/js/main.js` - hlavní JavaScript soubor
- `src/templates/` - HTML šablony

### Přidání nových funkcí

Pro přidání nových funkcí doporučujeme:
1. Vytvořit nový model v `src/models/`
2. Přidat nové routy v `src/routes/`
3. Vytvořit nové šablony v `src/templates/`

## 7. Nasazení do produkce

Pro nasazení do produkce doporučujeme:
1. Použít produkční WSGI server (např. Gunicorn nebo uWSGI)
2. Nastavit produkční databázi (MySQL nebo PostgreSQL)
3. Použít HTTPS pro zabezpečení komunikace
4. Nastavit správné proměnné prostředí

Příklad nasazení s Gunicorn:
```bash
pip install gunicorn
cd src
gunicorn -w 4 -b 0.0.0.0:8000 "main:create_app()"
```

## 8. Kontakt a podpora

Pokud máte jakékoliv dotazy nebo potřebujete pomoc, neváhejte nás kontaktovat:
- Email: podpora@factcheck.cz
- GitHub: vytvořte issue v repozitáři

---

Děkujeme, že používáte FactCheck! Společně můžeme bojovat proti dezinformacím a přispět k informovanější společnosti.
