"""
Inicializační soubor pro modely.

Tento modul poskytuje přístup k databázovým modelům aplikace.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import logging

# Nastavení loggeru
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializace SQLAlchemy - POUZE JEDNA INSTANCE PRO CELOU APLIKACI
db = SQLAlchemy()

# Definice modelů
class User(db.Model):
    """Model pro uživatele aplikace."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_supporter = db.Column(db.Boolean, default=False)
    support_level = db.Column(db.String(20), default=None)
    
    # Vztahy
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Analysis(db.Model):
    """Model pro analýzu tvrzení."""
    id = db.Column(db.Integer, primary_key=True)
    claim_text = db.Column(db.Text, nullable=False)
    verdict = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    analysis_type = db.Column(db.String(20), default='standard')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Vztahy
    evidences = db.relationship('Evidence', backref='analysis', lazy=True, cascade="all, delete-orphan")
    sources = db.relationship('Source', backref='analysis', lazy=True, cascade="all, delete-orphan")
    logical_fallacies = db.relationship('LogicalFallacy', backref='analysis', lazy=True, cascade="all, delete-orphan")
    manipulation_techniques = db.relationship('ManipulationTechnique', backref='analysis', lazy=True, cascade="all, delete-orphan")
    
    @classmethod
    def from_openai_response(cls, claim_text, response, analysis_type='standard', user_id=None):
        """
        Vytvoří instanci analýzy z odpovědi OpenAI API.
        
        Args:
            claim_text: Analyzované tvrzení
            response: Odpověď z OpenAI API
            analysis_type: Typ analýzy (standard, quick, detailed)
            user_id: ID uživatele, který analýzu vytvořil
            
        Returns:
            Instance Analysis
        """
        try:
            # Extrakce dat z odpovědi
            verdict = response.get('verdict', 'nelze ověřit')
            confidence = response.get('confidence', 50)
            explanation = response.get('explanation', 'Nebylo možné provést analýzu.')
            
            # Vytvoření instance analýzy
            analysis = cls(
                claim_text=claim_text,
                verdict=verdict,
                confidence=confidence,
                explanation=explanation,
                analysis_type=analysis_type,
                user_id=user_id
            )
            
            # Přidání důkazů
            evidences = response.get('evidences', [])
            if isinstance(evidences, list):
                for evidence_data in evidences:
                    if isinstance(evidence_data, dict):
                        text = evidence_data.get('text', '')
                    else:
                        text = str(evidence_data)
                    evidence = Evidence(text=text, analysis=analysis)
                    db.session.add(evidence)
            
            # Přidání zdrojů
            sources = response.get('sources', [])
            if isinstance(sources, list):
                for source_data in sources:
                    if isinstance(source_data, dict):
                        text = source_data.get('text', '')
                        url = source_data.get('url', '')
                    else:
                        text = str(source_data)
                        url = ''
                    source = Source(text=text, url=url, analysis=analysis)
                    db.session.add(source)
            
            # Přidání logických chyb
            fallacies = response.get('logical_fallacies', [])
            if isinstance(fallacies, list):
                for fallacy_data in fallacies:
                    if isinstance(fallacy_data, dict):
                        text = fallacy_data.get('text', '')
                        type_val = fallacy_data.get('type', '')
                    else:
                        text = str(fallacy_data)
                        type_val = ''
                    fallacy = LogicalFallacy(text=text, type=type_val, analysis=analysis)
                    db.session.add(fallacy)
            
            # Přidání manipulativních technik
            techniques = response.get('manipulation_techniques', [])
            if isinstance(techniques, list):
                for technique_data in techniques:
                    if isinstance(technique_data, dict):
                        text = technique_data.get('text', '')
                        type_val = technique_data.get('type', '')
                    else:
                        text = str(technique_data)
                        type_val = ''
                    technique = ManipulationTechnique(text=text, type=type_val, analysis=analysis)
                    db.session.add(technique)
            
            logger.info(f"Úspěšně vytvořena analýza pro tvrzení: {claim_text[:50]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"Chyba při vytváření analýzy: {str(e)}")
            # Vytvoření základní analýzy v případě chyby
            analysis = cls(
                claim_text=claim_text,
                verdict="nelze ověřit",
                confidence=0,
                explanation=f"Chyba při zpracování analýzy: {str(e)}",
                analysis_type=analysis_type,
                user_id=user_id
            )
            return analysis
    
    def __repr__(self):
        return f'<Analysis {self.id}>'

class Evidence(db.Model):
    """Model pro důkazy použité v analýze."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    
    def __repr__(self):
        return f'<Evidence {self.id}>'

class Source(db.Model):
    """Model pro zdroje použité v analýze."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    
    def __repr__(self):
        return f'<Source {self.id}>'

class LogicalFallacy(db.Model):
    """Model pro logické chyby identifikované v analýze."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    
    def __repr__(self):
        return f'<LogicalFallacy {self.id}>'

class ManipulationTechnique(db.Model):
    """Model pro manipulativní techniky identifikované v analýze."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    
    def __repr__(self):
        return f'<ManipulationTechnique {self.id}>'

class SupporterBenefit(db.Model):
    """Model pro výhody podporovatelů."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    support_level = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<SupporterBenefit {self.name}>'
