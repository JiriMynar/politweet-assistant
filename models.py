"""
Inicializační soubor pro modely.

Tento modul poskytuje přístup k databázovým modelům aplikace.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inicializace SQLAlchemy
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
        # V reálné aplikaci by zde byla logika pro zpracování odpovědi z API
        # Pro účely demonstrace používáme zjednodušenou verzi
        
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
        for evidence_data in response.get('evidences', []):
            evidence = Evidence(text=evidence_data.get('text', ''), analysis=analysis)
            db.session.add(evidence)
        
        # Přidání zdrojů
        for source_data in response.get('sources', []):
            source = Source(text=source_data.get('text', ''), url=source_data.get('url', ''), analysis=analysis)
            db.session.add(source)
        
        # Přidání logických chyb
        for fallacy_data in response.get('logical_fallacies', []):
            fallacy = LogicalFallacy(text=fallacy_data.get('text', ''), type=fallacy_data.get('type', ''), analysis=analysis)
            db.session.add(fallacy)
        
        # Přidání manipulativních technik
        for technique_data in response.get('manipulation_techniques', []):
            technique = ManipulationTechnique(text=technique_data.get('text', ''), type=technique_data.get('type', ''), analysis=analysis)
            db.session.add(technique)
        
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
