"""
Text Analyzer Module
-------------------
Modul pro analýzu textového obsahu, extrakci tvrzení a přípravu pro fact-checking.
"""

import re
import nltk
from nltk.tokenize import sent_tokenize
import logging

# Konfigurace logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stažení potřebných NLTK dat při prvním spuštění
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class TextAnalyzer:
    """
    Třída pro analýzu textového obsahu, identifikaci klíčových tvrzení a přípravu pro fact-checking.
    """
    
    def __init__(self):
        """Inicializace analyzátoru textového obsahu."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("TextAnalyzer inicializován")
    
    def analyze(self, text, expertise_level='medium', analysis_length='standard'):
        """
        Analyzuje textový obsah a identifikuje klíčová tvrzení k ověření.
        
        Args:
            text (str): Textový obsah k analýze
            expertise_level (str): Úroveň odbornosti analýzy ('basic', 'medium', 'advanced', 'expert')
            analysis_length (str): Požadovaná délka analýzy ('brief', 'standard', 'detailed', 'exhaustive')
            
        Returns:
            dict: Výsledky analýzy včetně identifikovaných tvrzení
        """
        self.logger.info(f"Začínám analýzu textu (délka: {len(text)} znaků)")
        
        # Kontrola prázdného vstupu
        if not text or not text.strip():
            return {
                'error': 'Prázdný vstupní text',
                'claims': [],
                'summary': 'Nebyl poskytnut žádný text k analýze.'
            }
        
        # Příprava textu
        cleaned_text = self._preprocess_text(text)
        
        # Rozdělení textu na věty
        sentences = sent_tokenize(cleaned_text)
        self.logger.info(f"Text rozdělen na {len(sentences)} vět")
        
        # Identifikace potenciálních tvrzení
        claims = self._identify_claims(sentences)
        self.logger.info(f"Identifikováno {len(claims)} potenciálních tvrzení")
        
        # Prioritizace tvrzení podle relevance
        prioritized_claims = self._prioritize_claims(claims)
        
        # Přizpůsobení počtu tvrzení podle požadované délky analýzy
        claims_limit = self._get_claims_limit(analysis_length)
        selected_claims = prioritized_claims[:claims_limit]
        
        # Vytvoření souhrnu
        summary = self._create_summary(cleaned_text)
        
        # Příprava výstupu
        result = {
            'claims': selected_claims,
            'summary': summary,
            'context': {
                'total_sentences': len(sentences),
                'total_claims_identified': len(claims),
                'selected_claims': len(selected_claims)
            }
        }
        
        self.logger.info("Analýza textu dokončena")
        return result
    
    def _preprocess_text(self, text):
        """
        Předzpracování textu - odstranění nadbytečných bílých znaků, normalizace apod.
        
        Args:
            text (str): Vstupní text
            
        Returns:
            str: Předzpracovaný text
        """
        # Odstranění nadbytečných bílých znaků
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        # Normalizace uvozovek
        cleaned_text = re.sub(r'["""]', '"', cleaned_text)
        
        return cleaned_text
    
    def _identify_claims(self, sentences):
        """
        Identifikace potenciálních tvrzení ve větách.
        
        Args:
            sentences (list): Seznam vět
            
        Returns:
            list: Seznam identifikovaných tvrzení
        """
        claims = []
        
        # Klíčová slova a fráze, které mohou indikovat faktické tvrzení
        claim_indicators = [
            r'\b(je|jsou|byl|byla|bylo|byly)\b',
            r'\b(má|mají|měl|měla|mělo|měly)\b',
            r'\b(podle|dle)\b',
            r'\b(studie|výzkum|analýza|zpráva)\b',
            r'\b(prokázal|prokázala|prokázalo|prokázaly)\b',
            r'\b(zjistil|zjistila|zjistilo|zjistily)\b',
            r'\b(tvrdí|uvedl|uvedla|uvedlo|uvedly)\b',
            r'\b(fakt|faktem|fakta|faktů)\b',
            r'\b(procent|%)\b',
            r'\b(tisíc|milion|miliard)\b',
            r'\b(v roce|v letech)\b',
            r'\b(vzrostl|vzrostla|vzrostlo|vzrostly|klesl|klesla|kleslo|klesly)\b'
        ]
        
        for i, sentence in enumerate(sentences):
            # Kontrola, zda věta obsahuje některý z indikátorů tvrzení
            is_claim = any(re.search(pattern, sentence.lower()) for pattern in claim_indicators)
            
            # Kontrola délky věty (příliš krátké věty pravděpodobně neobsahují ověřitelná tvrzení)
            if len(sentence.split()) < 3:
                is_claim = False
            
            # Kontrola, zda věta obsahuje čísla (často indikátor faktického tvrzení)
            contains_numbers = bool(re.search(r'\d+', sentence))
            
            # Kontrola, zda věta obsahuje vlastní jména (často indikátor faktického tvrzení)
            contains_proper_nouns = bool(re.search(r'[A-Z][a-z]+', sentence))
            
            # Přidání skóre relevance
            relevance_score = 0
            if is_claim:
                relevance_score += 2
            if contains_numbers:
                relevance_score += 1
            if contains_proper_nouns:
                relevance_score += 1
            
            # Pokud má věta dostatečné skóre relevance, považujeme ji za potenciální tvrzení
            if relevance_score >= 1:
                claims.append({
                    'text': sentence,
                    'position': i,
                    'relevance_score': relevance_score
                })
        
        return claims
    
    def _prioritize_claims(self, claims):
        """
        Prioritizace tvrzení podle relevance.
        
        Args:
            claims (list): Seznam identifikovaných tvrzení
            
        Returns:
            list: Seznam prioritizovaných tvrzení
        """
        # Seřazení tvrzení podle skóre relevance (sestupně)
        prioritized = sorted(claims, key=lambda x: x['relevance_score'], reverse=True)
        
        return prioritized
    
    def _get_claims_limit(self, analysis_length):
        """
        Určení limitu počtu tvrzení podle požadované délky analýzy.
        
        Args:
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            int: Limit počtu tvrzení
        """
        limits = {
            'brief': 3,
            'standard': 5,
            'detailed': 8,
            'exhaustive': 12
        }
        
        return limits.get(analysis_length, 5)
    
    def _create_summary(self, text):
        """
        Vytvoření souhrnu analyzovaného obsahu.
        
        Args:
            text (str): Analyzovaný text
            
        Returns:
            str: Souhrn obsahu
        """
        # Zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        words = text.split()
        word_count = len(words)
        
        # Vytvoření jednoduchého souhrnu
        if word_count <= 50:
            return f"Krátký text o délce {word_count} slov."
        elif word_count <= 200:
            return f"Text střední délky obsahující {word_count} slov."
        else:
            return f"Dlouhý text obsahující {word_count} slov."
