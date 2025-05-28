"""
Model pro analýzu tvrzení.

Tento modul definuje datové struktury pro ukládání analýz tvrzení.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Analysis(db.Model):
    """Model pro ukládání výsledků analýz tvrzení."""
    
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    claim_text = Column(Text, nullable=False)
    verdict = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    analysis_type = Column(String(20), default="standard")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Vztahy
    user = relationship("User", back_populates="analyses")
    evidences = relationship("Evidence", back_populates="analysis", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="analysis", cascade="all, delete-orphan")
    logical_fallacies = relationship("LogicalFallacy", back_populates="analysis", cascade="all, delete-orphan")
    manipulation_techniques = relationship("ManipulationTechnique", back_populates="analysis", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Převede model na slovník."""
        return {
            'id': self.id,
            'claim_text': self.claim_text,
            'verdict': self.verdict,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'analysis_type': self.analysis_type,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'evidences': [evidence.text for evidence in self.evidences],
            'sources': [source.text for source in self.sources],
            'logical_fallacies': [fallacy.text for fallacy in self.logical_fallacies],
            'manipulation_techniques': [technique.text for technique in self.manipulation_techniques]
        }
    
    @classmethod
    def from_openai_response(cls, claim_text: str, response: dict, analysis_type: str = "standard", user_id: Optional[int] = None):
        """
        Vytvoří instanci analýzy z odpovědi OpenAI API.
        
        Args:
            claim_text: Analyzované tvrzení
            response: Odpověď z OpenAI API
            analysis_type: Typ analýzy
            user_id: ID uživatele (volitelné)
            
        Returns:
            Instance Analysis
        """
        analysis = cls(
            claim_text=claim_text,
            verdict=response.get('verdict', 'nelze určit'),
            confidence=response.get('confidence', 0),
            explanation=response.get('explanation', ''),
            analysis_type=analysis_type,
            user_id=user_id
        )
        
        # Přidání důkazů
        for evidence_text in response.get('evidence', []):
            if evidence_text:
                analysis.evidences.append(Evidence(text=evidence_text))
        
        # Přidání zdrojů
        for source_text in response.get('sources', []):
            if source_text:
                analysis.sources.append(Source(text=source_text))
        
        # Přidání logických chyb
        for fallacy_text in response.get('logical_fallacies', []):
            if fallacy_text:
                analysis.logical_fallacies.append(LogicalFallacy(text=fallacy_text))
        
        # Přidání manipulativních technik
        for technique_text in response.get('manipulation_techniques', []):
            if technique_text:
                analysis.manipulation_techniques.append(ManipulationTechnique(text=technique_text))
        
        return analysis


class Evidence(db.Model):
    """Model pro ukládání důkazů k analýze."""
    
    __tablename__ = 'evidences'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    
    # Vztahy
    analysis = relationship("Analysis", back_populates="evidences")


class Source(db.Model):
    """Model pro ukládání zdrojů k analýze."""
    
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    
    # Vztahy
    analysis = relationship("Analysis", back_populates="sources")


class LogicalFallacy(db.Model):
    """Model pro ukládání logických chyb k analýze."""
    
    __tablename__ = 'logical_fallacies'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    
    # Vztahy
    analysis = relationship("Analysis", back_populates="logical_fallacies")


class ManipulationTechnique(db.Model):
    """Model pro ukládání manipulativních technik k analýze."""
    
    __tablename__ = 'manipulation_techniques'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    analysis_id = Column(Integer, ForeignKey('analyses.id'), nullable=False)
    
    # Vztahy
    analysis = relationship("Analysis", back_populates="manipulation_techniques")


class User(db.Model):
    """Model pro ukládání uživatelů."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_supporter = Column(Boolean, default=False)
    support_level = Column(String(20), nullable=True)
    
    # Vztahy
    analyses = relationship("Analysis", back_populates="user")
    
    def to_dict(self):
        """Převede model na slovník."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_supporter': self.is_supporter,
            'support_level': self.support_level
        }


class SupporterBenefit(db.Model):
    """Model pro ukládání výhod pro podporovatele."""
    
    __tablename__ = 'supporter_benefits'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    support_level = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        """Převede model na slovník."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'support_level': self.support_level,
            'is_active': self.is_active
        }
