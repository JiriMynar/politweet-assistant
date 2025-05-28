"""
Inicializační soubor pro routy.

Tento modul poskytuje přístup k blueprintům aplikace.
"""

from src.routes.main import main_bp
from src.routes.auth import auth_bp
from src.routes.factcheck import factcheck_bp
from src.routes.support import support_bp
from src.routes.education import education_bp

__all__ = [
    "main_bp",
    "auth_bp",
    "factcheck_bp",
    "support_bp",
    "education_bp"
]
