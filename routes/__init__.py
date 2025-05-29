"""
Inicializační soubor pro routy.

Tento modul poskytuje přístup k blueprintům aplikace.
"""

from flask import Blueprint

# Vytvoření blueprintů
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
factcheck_bp = Blueprint('factcheck', __name__)
support_bp = Blueprint('support', __name__)
education_bp = Blueprint('education', __name__)

# Import rout pro jednotlivé blueprinty
from routes.main import *
from routes.auth import *
from routes.factcheck import *
from routes.support import *
from routes.education import *
