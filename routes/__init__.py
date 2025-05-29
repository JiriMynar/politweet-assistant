"""
Inicializační soubor pro routes.

Tento modul poskytuje přístup k blueprintům aplikace.
"""

from routes.main import main_bp
from routes.auth import auth_bp
from routes.factcheck import factcheck_bp
from routes.support import support_bp
from routes.education import education_bp

__all__ = ["main_bp", "auth_bp", "factcheck_bp", "support_bp", "education_bp"]
