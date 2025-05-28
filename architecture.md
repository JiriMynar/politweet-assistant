# Architektura webové aplikace pro fact-checking

## Přehled

Tato webová aplikace je navržena jako komplexní nástroj pro ověřování faktů s využitím OpenAI API. Aplikace poskytuje uživatelům možnost ověřovat tvrzení, vzdělávat se v oblasti mediální gramotnosti a podporovat projekt finančními příspěvky.

## Struktura aplikace

### 1. Základní komponenty

#### Backend (Flask)
- **Hlavní aplikace** (`src/main.py`) - Vstupní bod aplikace, konfigurace
- **Modely** (`src/models/`) - Databázové modely pro ukládání dat
- **Routy** (`src/routes/`) - API endpointy a webové stránky
- **Služby** (`src/services/`) - Byznys logika, integrace s OpenAI API

#### Frontend
- **Šablony** (`src/templates/`) - Jinja2 šablony pro vykreslování stránek
- **Statické soubory** (`src/static/`) - CSS, JavaScript, obrázky
- **Komponenty** - Znovupoužitelné UI prvky

### 2. Hlavní moduly

#### Fact-checking modul
- **Analýza tvrzení** - Zpracování uživatelských vstupů
- **OpenAI integrace** - Komunikace s OpenAI API
- **Vyhodnocení výsledků** - Zpracování odpovědí z API
- **Prezentace výsledků** - Zobrazení výsledků uživateli

#### Vzdělávací modul
- **Průvodce mediální gramotností** - Vzdělávací materiály
- **Interaktivní ukázky** - Příklady dezinformací a jejich analýzy
- **Tipy pro rozpoznávání dezinformací** - Praktické rady

#### Modul podpory projektu
- **Platební integrace** - Zpracování plateb
- **Správa výhod** - Přidělování výhod podporovatelům
- **Transparentní reporting** - Informace o využití prostředků

#### Uživatelský modul
- **Správa účtů** - Registrace, přihlášení, profily
- **Historie analýz** - Ukládání a zobrazení předchozích analýz
- **Nastavení** - Uživatelské preference

## Datový model

### Uživatelé
- ID, jméno, email, heslo, role, datum registrace
- Vztah k podporovatelům a analýzám

### Analýzy
- ID, text tvrzení, výsledek, vysvětlení, datum, uživatel
- Vztah k uživateli a zdrojům

### Podporovatelé
- ID, uživatel, úroveň podpory, částka, datum, status
- Vztah k uživateli a výhodám

### Výhody
- ID, název, popis, podmínky, aktivní
- Vztah k úrovním podpory

## Uživatelské rozhraní

### Hlavní stránka
- Vstupní pole pro zadání tvrzení
- Tlačítko pro spuštění analýzy
- Ukázky předchozích analýz
- Informace o projektu

### Stránka s výsledky analýzy
- Verdikt o pravdivosti
- Vizuální indikátor (barevné označení)
- Podrobné vysvětlení
- Zdroje a důkazy
- Možnost sdílení a exportu

### Sekce podpory projektu
- Informace o nákladech a využití prostředků
- Možnosti jednorázových a pravidelných příspěvků
- Přehled výhod pro podporovatele
- Platební formuláře

### Vzdělávací sekce
- Články o mediální gramotnosti
- Interaktivní ukázky dezinformací
- Návody na rozpoznávání manipulativních technik
- Kvízy a testy

### Uživatelský profil
- Historie analýz
- Status podporovatele
- Dostupné výhody
- Nastavení účtu

## Technické detaily

### Integrace s OpenAI API
- Bezpečná správa API klíče
- Optimalizace promptů pro přesné výsledky
- Cachování pro snížení nákladů
- Záložní strategie při nedostupnosti API

### Bezpečnost
- Šifrování citlivých dat
- Ochrana proti CSRF, XSS a SQL injection
- Bezpečné ukládání hesel
- Rate limiting pro prevenci zneužití

### Výkon
- Cachování častých dotazů
- Asynchronní zpracování dlouhotrvajících operací
- Optimalizace databázových dotazů
- Lazy loading pro rychlé načítání stránek

### Responzivní design
- Optimalizace pro mobilní zařízení
- Přizpůsobení UI pro různé velikosti obrazovek
- Dotyková podpora pro mobilní uživatele

## Uživatelské cesty

### Základní fact-checking
1. Uživatel navštíví hlavní stránku
2. Zadá tvrzení k ověření
3. Systém zpracuje tvrzení pomocí OpenAI API
4. Uživatel obdrží výsledek analýzy
5. Má možnost prozkoumat detaily, zdroje a vysvětlení

### Podpora projektu
1. Uživatel klikne na "Podpořit projekt"
2. Prohlédne si možnosti podpory
3. Vybere typ a výši příspěvku
4. Dokončí platbu
5. Obdrží potvrzení a informace o výhodách

### Vzdělávání
1. Uživatel navštíví vzdělávací sekci
2. Prohlíží si materiály o mediální gramotnosti
3. Zkouší interaktivní ukázky
4. Testuje své znalosti v kvízech
5. Získává tipy pro rozpoznávání dezinformací

## Vizuální design

### Barevné schéma
- Primární barva: #2D3E50 (tmavě modrá) - důvěryhodnost, stabilita
- Sekundární barva: #3498DB (světle modrá) - přístupnost, klid
- Akcentová barva: #E74C3C (červená) - důležité informace, varování
- Akcentová barva pro podporu: #7B61FF (fialová) - štědrost, kreativita

### Typografie
- Nadpisy: Roboto, sans-serif
- Tělo textu: Open Sans, sans-serif
- Monospace: Source Code Pro (pro technické detaily)

### UI komponenty
- Zaoblené rohy pro karty a tlačítka
- Jemné stíny pro hierarchii prvků
- Animace pro interaktivní prvky
- Ikony pro intuitivní navigaci

## Implementační priority

1. Základní fact-checking funkcionalita
2. Integrace s OpenAI API
3. Prezentace výsledků analýzy
4. Vzdělávací komponenty
5. Sekce podpory projektu
6. Uživatelské účty a historie
7. Mobilní optimalizace
8. Gamifikační prvky
