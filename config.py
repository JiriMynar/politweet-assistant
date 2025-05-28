"""
Konfigurační soubor pro aplikaci FactCheck.

Tento soubor obsahuje konfigurační proměnné pro aplikaci.
"""

import os

# Základní konfigurace
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'faktchek-tajny-klic-pro-vyvoj')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Konfigurace databáze
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///factcheck.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Konfigurace aplikace
APP_NAME = 'FactCheck'
APP_DESCRIPTION = 'Ověřování faktů pomocí umělé inteligence'
APP_VERSION = '1.0.0'
APP_AUTHOR = 'FactCheck Team'
APP_CONTACT_EMAIL = 'info@factcheck.cz'

# Konfigurace OpenAI
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')
OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.1'))
OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '2000'))

# Konfigurace analýzy
ANALYSIS_TYPES = {
    'quick': {
        'name': 'Rychlá analýza',
        'description': 'Základní analýza s verdiktem a krátkým vysvětlením',
        'max_tokens': 1000,
        'requires_supporter': False,
        'price': 0
    },
    'standard': {
        'name': 'Standardní analýza',
        'description': 'Podrobná analýza s verdiktem, vysvětlením a identifikací logických chyb',
        'max_tokens': 2000,
        'requires_supporter': False,
        'price': 0
    },
    'detailed': {
        'name': 'Detailní analýza',
        'description': 'Velmi podrobná analýza s kontextem, alternativními interpretacemi a detailním vysvětlením',
        'max_tokens': 4000,
        'requires_supporter': True,
        'price': 0
    }
}

# Konfigurace podpory projektu
SUPPORT_LEVELS = {
    'bronze': {
        'name': 'Bronzový podporovatel',
        'price': 99,
        'period': 'měsíčně',
        'benefits': [
            'Přístup k detailní analýze',
            'Bez reklam',
            'Historie analýz (až 10 položek)'
        ]
    },
    'silver': {
        'name': 'Stříbrný podporovatel',
        'price': 199,
        'period': 'měsíčně',
        'benefits': [
            'Přístup k detailní analýze',
            'Bez reklam',
            'Historie analýz (až 50 položek)',
            'Export výsledků do PDF'
        ]
    },
    'gold': {
        'name': 'Zlatý podporovatel',
        'price': 399,
        'period': 'měsíčně',
        'benefits': [
            'Přístup k detailní analýze',
            'Bez reklam',
            'Neomezená historie analýz',
            'Export výsledků do PDF',
            'Prioritní zpracování',
            'Přístup k beta funkcím'
        ]
    }
}
