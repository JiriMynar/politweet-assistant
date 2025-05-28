"""
Inicializační soubor pro modely.

Tento modul poskytuje přístup k databázovým modelům aplikace.
"""

from src.models.models import db, Analysis, Evidence, Source, LogicalFallacy, ManipulationTechnique, User, SupporterBenefit

__all__ = [
    "db", 
    "Analysis", 
    "Evidence", 
    "Source", 
    "LogicalFallacy", 
    "ManipulationTechnique", 
    "User", 
    "SupporterBenefit"
]
