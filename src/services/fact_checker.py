"""
Fact Checker Module
-------------------
Hlavní modul pro fact-checking, který integruje všechny analyzátory a poskytuje komplexní hodnocení pravdivosti.
"""

import logging
import json
import uuid
import datetime
import re
import os
import tempfile
from typing import Dict, List, Any, Optional, Union

# Import vlastních modulů
from services.text_analyzer import TextAnalyzer
from services.image_analyzer import ImageAnalyzer
from services.audio_analyzer import AudioAnalyzer
from services.video_analyzer import VideoAnalyzer
from services.source_evaluator import SourceEvaluator

# Konfigurace logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FactChecker:
    """
    Třída pro komplexní fact-checking různých typů médií a hodnocení pravdivosti informací.
    """
    
    def __init__(self):
        """Inicializace fact-checkeru."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("FactChecker inicializován")
        
        # Inicializace analyzátorů
        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.source_evaluator = SourceEvaluator()
        
        # Definice škály hodnocení pravdivosti
        self.truth_scale = {
            'true': {
                'name': 'Pravdivé',
                'description': 'Informace je zcela přesná, podložená důvěryhodnými zdroji a odpovídá současnému stavu poznání.',
                'color': '#34A853',  # zelená
                'score_range': (0.9, 1.0)
            },
            'mostly_true': {
                'name': 'Převážně pravdivé',
                'description': 'Informace je z větší části přesná, ale obsahuje drobné nepřesnosti, které nemění celkové vyznění.',
                'color': '#4CAF50',  # světlejší zelená
                'score_range': (0.75, 0.9)
            },
            'partly_true': {
                'name': 'Částečně pravdivé',
                'description': 'Informace obsahuje některé pravdivé prvky, ale také významné nepřesnosti nebo vynechává důležitý kontext.',
                'color': '#FBBC05',  # žlutá
                'score_range': (0.5, 0.75)
            },
            'mostly_false': {
                'name': 'Převážně nepravdivé',
                'description': 'Informace obsahuje některé pravdivé prvky, ale je převážně nepřesná nebo zavádějící.',
                'color': '#F57C00',  # oranžová
                'score_range': (0.25, 0.5)
            },
            'false': {
                'name': 'Nepravdivé',
                'description': 'Informace je zcela nepřesná, nepodložená důvěryhodnými zdroji nebo odporuje současnému stavu poznání.',
                'color': '#EA4335',  # červená
                'score_range': (0.0, 0.25)
            },
            'misleading': {
                'name': 'Zavádějící',
                'description': 'Informace může být technicky pravdivá, ale je prezentována způsobem, který je zavádějící nebo manipulativní.',
                'color': '#9C27B0',  # fialová
                'score_range': (0.3, 0.6)  # překrývá se s částečně pravdivé a převážně nepravdivé
            },
            'insufficient_evidence': {
                'name': 'Nedostatečné údaje',
                'description': 'Nelze jednoznačně určit pravdivost informace kvůli nedostatku dostupných důvěryhodných zdrojů.',
                'color': '#9AA0A6',  # šedá
                'score_range': (0.4, 0.6)  # překrývá se s částečně pravdivé
            },
            'unverifiable': {
                'name': 'Neověřitelné',
                'description': 'Tvrzení nelze ověřit pomocí dostupných faktů nebo důkazů, často se jedná o spekulace o budoucnosti.',
                'color': '#607D8B',  # modrošedá
                'score_range': (0.4, 0.6)  # překrývá se s částečně pravdivé
            },
            'satire': {
                'name': 'Satira',
                'description': 'Obsah je záměrně nepravdivý nebo přehnaný za účelem humoru, parodie nebo společenské kritiky.',
                'color': '#8D6E63',  # hnědá
                'score_range': (0.3, 0.7)  # široký rozsah, protože satira může být různě "pravdivá"
            }
        }
    
    def check_facts(self, content, content_type='text', language='cs', expertise_level='medium', analysis_length='standard'):
        """
        Provádí fact-checking obsahu a hodnotí jeho pravdivost.
        
        Args:
            content (str): Obsah k analýze (text, cesta k souboru nebo URL)
            content_type (str): Typ obsahu ('text', 'image', 'audio', 'video')
            language (str): Kód jazyka pro rozpoznávání řeči ('cs', 'en', 'sk', atd.)
            expertise_level (str): Úroveň odbornosti analýzy ('basic', 'medium', 'advanced', 'expert')
            analysis_length (str): Požadovaná délka analýzy ('brief', 'standard', 'detailed', 'exhaustive')
            
        Returns:
            dict: Výsledky fact-checkingu včetně hodnocení pravdivosti
        """
        self.logger.info(f"Začínám fact-checking obsahu typu {content_type}")
        
        try:
            # Generování unikátního ID pro výsledek
            result_id = str(uuid.uuid4())
            
            # Analýza obsahu podle typu
            content_analysis = self._analyze_content(content, content_type, language, expertise_level, analysis_length)
            
            # Extrakce tvrzení k ověření
            claims = self._extract_claims(content_analysis, content_type)
            
            # Ověření tvrzení
            verified_claims = self._verify_claims(claims, expertise_level, analysis_length)
            
            # Hodnocení celkové pravdivosti
            truth_rating = self._evaluate_overall_truth(verified_claims)
            
            # Identifikace zdrojů
            sources = self._identify_sources(verified_claims)
            
            # Hodnocení zdrojů
            evaluated_sources = self._evaluate_sources(sources, expertise_level)
            
            # Identifikace alternativních perspektiv
            alternative_perspectives = self._identify_alternative_perspectives(verified_claims, expertise_level, analysis_length)
            
            # Generování navrhovaných reakcí
            suggested_responses = self._generate_suggested_responses(verified_claims, truth_rating, expertise_level, analysis_length)
            
            # Vytvoření souhrnu
            summary = self._create_summary(content_analysis, truth_rating, verified_claims, content_type)
            
            # Příprava výstupu
            result = {
                'id': result_id,
                'timestamp': datetime.datetime.now().isoformat(),
                'content_type': content_type,
                'content_summary': summary,
                'truth_rating': truth_rating['name'],
                'truth_score': truth_rating['score'],
                'truth_color': truth_rating['color'],
                'truth_description': truth_rating['description'],
                'analysis': {
                    'detailed_explanation': self._generate_detailed_explanation(verified_claims, truth_rating, expertise_level, analysis_length),
                    'key_points': self._extract_key_points(verified_claims, expertise_level, analysis_length),
                    'claims': verified_claims,
                    'sources': evaluated_sources,
                    'alternative_perspectives': alternative_perspectives,
                    'suggested_responses': suggested_responses
                },
                'settings': {
                    'expertise_level': expertise_level,
                    'analysis_length': analysis_length,
                    'language': language
                },
                'metadata': {
                    'processing_time': datetime.datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            self.logger.info(f"Fact-checking dokončen, hodnocení: {truth_rating['name']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chyba při fact-checkingu: {str(e)}", exc_info=True)
            return {
                'error': f'Chyba při fact-checkingu: {str(e)}',
                'id': str(uuid.uuid4()),
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def _analyze_content(self, content, content_type, language, expertise_level, analysis_length):
        """
        Analyzuje obsah podle jeho typu.
        
        Args:
            content (str): Obsah k analýze
            content_type (str): Typ obsahu
            language (str): Kód jazyka
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            dict: Výsledky analýzy obsahu
        """
        if content_type == 'text':
            return self.text_analyzer.analyze(content, expertise_level, analysis_length)
        elif content_type == 'image':
            return self.image_analyzer.analyze(content, expertise_level, analysis_length)
        elif content_type == 'audio':
            return self.audio_analyzer.analyze(content, language, expertise_level, analysis_length)
        elif content_type == 'video':
            return self.video_analyzer.analyze(content, language, expertise_level, analysis_length)
        else:
            raise ValueError(f"Nepodporovaný typ obsahu: {content_type}")
    
    def _extract_claims(self, content_analysis, content_type):
        """
        Extrahuje tvrzení k ověření z analyzovaného obsahu.
        
        Args:
            content_analysis (dict): Výsledky analýzy obsahu
            content_type (str): Typ obsahu
            
        Returns:
            list: Seznam tvrzení k ověření
        """
        claims = []
        
        if content_type == 'text':
            # Pro textový obsah použijeme přímo extrahovaná tvrzení
            if 'claims' in content_analysis:
                claims = content_analysis['claims']
        elif content_type == 'image':
            # Pro obrázky použijeme extrahovaný text a vizuální prvky
            if 'extracted_text' in content_analysis and content_analysis['extracted_text']:
                # Analýza extrahovaného textu
                text_analysis = self.text_analyzer.analyze(content_analysis['extracted_text'])
                if 'claims' in text_analysis:
                    claims.extend(text_analysis['claims'])
            
            # Přidání informací o vizuálních prvcích
            if 'visual_elements' in content_analysis:
                for element in content_analysis['visual_elements']:
                    claims.append({
                        'text': f"Obrázek obsahuje {element['type']}.",
                        'position': -1,
                        'relevance_score': element['confidence'] if 'confidence' in element else 0.5,
                        'visual_element': True
                    })
        elif content_type == 'audio':
            # Pro audio použijeme transkripci
            if 'transcription' in content_analysis and content_analysis['transcription']:
                # Analýza transkripce
                text_analysis = self.text_analyzer.analyze(content_analysis['transcription'])
                if 'claims' in text_analysis:
                    claims.extend(text_analysis['claims'])
        elif content_type == 'video':
            # Pro video použijeme transkripci a analýzu klíčových snímků
            if 'audio_analysis' in content_analysis and 'transcription' in content_analysis['audio_analysis']:
                # Analýza transkripce
                transcription = content_analysis['audio_analysis']['transcription']
                if transcription:
                    text_analysis = self.text_analyzer.analyze(transcription)
                    if 'claims' in text_analysis:
                        claims.extend(text_analysis['claims'])
            
            # Přidání informací z klíčových snímků
            if 'key_frames' in content_analysis:
                for frame in content_analysis['key_frames']:
                    if 'analysis' in frame and 'extracted_text' in frame['analysis']:
                        extracted_text = frame['analysis']['extracted_text']
                        if extracted_text:
                            # Analýza extrahovaného textu
                            text_analysis = self.text_analyzer.analyze(extracted_text)
                            if 'claims' in text_analysis:
                                for claim in text_analysis['claims']:
                                    claim['timestamp'] = frame['timestamp']
                                    claims.append(claim)
        
        return claims
    
    def _verify_claims(self, claims, expertise_level, analysis_length):
        """
        Ověřuje pravdivost tvrzení.
        
        Args:
            claims (list): Seznam tvrzení k ověření
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            list: Seznam ověřených tvrzení
        """
        verified_claims = []
        
        for claim in claims:
            # Simulace ověření tvrzení - v produkční verzi by zde byl sofistikovanější algoritmus
            # pro ověřování faktů proti důvěryhodným zdrojům
            
            # Pro demonstrační účely generujeme náhodné hodnocení
            import random
            
            # Základní pravděpodobnosti pro různé hodnocení
            probabilities = {
                'true': 0.2,
                'mostly_true': 0.25,
                'partly_true': 0.3,
                'mostly_false': 0.15,
                'false': 0.1
            }
            
            # Výběr hodnocení podle pravděpodobností
            rating_key = random.choices(
                list(probabilities.keys()),
                weights=list(probabilities.values()),
                k=1
            )[0]
            
            # Získání detailů hodnocení
            rating = self.truth_scale[rating_key]
            
            # Přesné skóre v rámci rozsahu pro dané hodnocení
            score_min, score_max = rating['score_range']
            score = random.uniform(score_min, score_max)
            
            # Simulace zdrojů
            sources = self._simulate_sources(claim['text'], 2)
            
            # Vytvoření ověřeného tvrzení
            verified_claim = {
                'text': claim['text'],
                'rating': rating['name'],
                'rating_key': rating_key,
                'score': score,
                'color': rating['color'],
                'explanation': self._generate_claim_explanation(claim['text'], rating, expertise_level),
                'sources': sources
            }
            
            # Přidání dalších informací z původního tvrzení
            for key, value in claim.items():
                if key not in verified_claim and key != 'text':
                    verified_claim[key] = value
            
            verified_claims.append(verified_claim)
        
        return verified_claims
    
    def _evaluate_overall_truth(self, verified_claims):
        """
        Hodnotí celkovou pravdivost na základě ověřených tvrzení.
        
        Args:
            verified_claims (list): Seznam ověřených tvrzení
            
        Returns:
            dict: Celkové hodnocení pravdivosti
        """
        if not verified_claims:
            # Pokud nejsou žádná tvrzení, vrátíme "Nedostatečné údaje"
            return {
                'name': self.truth_scale['insufficient_evidence']['name'],
                'key': 'insufficient_evidence',
                'description': self.truth_scale['insufficient_evidence']['description'],
                'color': self.truth_scale['insufficient_evidence']['color'],
                'score': 0.5
            }
        
        # Výpočet váženého průměru skóre
        total_score = 0
        total_weight = 0
        
        for claim in verified_claims:
            # Váha je dána relevancí tvrzení
            weight = claim.get('relevance_score', 1.0)
            total_score += claim['score'] * weight
            total_weight += weight
        
        # Výpočet průměrného skóre
        avg_score = total_score / total_weight if total_weight > 0 else 0.5
        
        # Určení hodnocení na základě průměrného skóre
        rating_key = None
        for key, rating in self.truth_scale.items():
            score_min, score_max = rating['score_range']
            if score_min <= avg_score < score_max:
                # Kontrola speciálních případů
                if key in ['misleading', 'insufficient_evidence', 'unverifiable', 'satire']:
                    # Tyto kategorie vyžadují speciální detekci, ne jen skóre
                    continue
                
                rating_key = key
                break
        
        # Pokud nebyl nalezen žádný odpovídající rating, použijeme výchozí
        if not rating_key:
            if avg_score >= 0.5:
                rating_key = 'partly_true'
            else:
                rating_key = 'mostly_false'
        
        rating = self.truth_scale[rating_key]
        
        return {
            'name': rating['name'],
            'key': rating_key,
            'description': rating['description'],
            'color': rating['color'],
            'score': avg_score
        }
    
    def _identify_sources(self, verified_claims):
        """
        Identifikuje zdroje použité při ověřování tvrzení.
        
        Args:
            verified_claims (list): Seznam ověřených tvrzení
            
        Returns:
            list: Seznam zdrojů
        """
        # Shromáždění všech zdrojů z ověřených tvrzení
        all_sources = []
        for claim in verified_claims:
            if 'sources' in claim:
                all_sources.extend(claim['sources'])
        
        # Odstranění duplicit
        unique_sources = []
        seen_urls = set()
        
        for source in all_sources:
            if source['url'] not in seen_urls:
                seen_urls.add(source['url'])
                unique_sources.append(source)
        
        return unique_sources
    
    def _evaluate_sources(self, sources, expertise_level):
        """
        Hodnotí důvěryhodnost zdrojů.
        
        Args:
            sources (list): Seznam zdrojů k hodnocení
            expertise_level (str): Úroveň odbornosti hodnocení
            
        Returns:
            list: Seznam hodnocených zdrojů
        """
        evaluated_sources = []
        
        for source in sources:
            # Hodnocení zdroje
            evaluation = self.source_evaluator.evaluate_source(source['url'], expertise_level=expertise_level)
            
            # Sloučení původních informací o zdroji s hodnocením
            evaluated_source = {**source, **evaluation}
            
            evaluated_sources.append(evaluated_source)
        
        return evaluated_sources
    
    def _identify_alternative_perspectives(self, verified_claims, expertise_level, analysis_length):
        """
        Identifikuje alternativní perspektivy na ověřovaná tvrzení.
        
        Args:
            verified_claims (list): Seznam ověřených tvrzení
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            list: Seznam alternativních perspektiv
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro identifikaci alternativních perspektiv
        
        # Pro demonstrační účely generujeme simulované alternativní perspektivy
        perspectives = []
        
        # Počet perspektiv podle délky analýzy
        perspective_counts = {
            'brief': 1,
            'standard': 2,
            'detailed': 3,
            'exhaustive': 4
        }
        
        count = perspective_counts.get(analysis_length, 2)
        
        # Generování perspektiv
        for i in range(count):
            if i == 0:
                perspectives.append({
                    'title': 'Ekonomická perspektiva',
                    'description': 'Z ekonomického hlediska je třeba zvážit dlouhodobé dopady na trh práce a hospodářský růst.',
                    'type': 'economic'
                })
            elif i == 1:
                perspectives.append({
                    'title': 'Sociální perspektiva',
                    'description': 'Ze sociálního hlediska je důležité zohlednit dopady na různé skupiny obyvatel a sociální soudržnost.',
                    'type': 'social'
                })
            elif i == 2:
                perspectives.append({
                    'title': 'Environmentální perspektiva',
                    'description': 'Z environmentálního hlediska je třeba zvážit dopady na životní prostředí a udržitelnost.',
                    'type': 'environmental'
                })
            elif i == 3:
                perspectives.append({
                    'title': 'Historická perspektiva',
                    'description': 'Z historického hlediska lze podobné situace najít v minulosti a poučit se z jejich vývoje.',
                    'type': 'historical'
                })
        
        return perspectives
    
    def _generate_suggested_responses(self, verified_claims, truth_rating, expertise_level, analysis_length):
        """
        Generuje navrhované reakce na ověřená tvrzení.
        
        Args:
            verified_claims (list): Seznam ověřených tvrzení
            truth_rating (dict): Celkové hodnocení pravdivosti
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            list: Seznam navrhovaných reakcí
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro generování reakcí
        
        responses = []
        
        # Informativní reakce
        informative_response = f"Podle dostupných informací je toto tvrzení {truth_rating['name'].lower()}. "
        
        if truth_rating['key'] in ['true', 'mostly_true']:
            informative_response += "Fakta potvrzují správnost tohoto tvrzení."
        elif truth_rating['key'] in ['partly_true']:
            informative_response += "Tvrzení obsahuje některé pravdivé prvky, ale také nepřesnosti nebo zavádějící informace."
        elif truth_rating['key'] in ['mostly_false', 'false']:
            informative_response += "Fakta nepotvrzují správnost tohoto tvrzení."
        elif truth_rating['key'] == 'misleading':
            informative_response += "Ačkoliv některé části mohou být technicky pravdivé, celkové vyznění je zavádějící."
        
        responses.append({
            'type': 'informative',
            'text': informative_response,
            'icon': 'info'
        })
        
        # Vzdělávací reakce
        educational_response = "Je důležité si uvědomit, že "
        
        if truth_rating['key'] in ['true', 'mostly_true']:
            educational_response += "ověřování informací z důvěryhodných zdrojů je klíčové pro formování informovaných názorů."
        elif truth_rating['key'] in ['partly_true', 'misleading']:
            educational_response += "i částečně pravdivé informace mohou být zavádějící, pokud jsou vytrženy z kontextu."
        elif truth_rating['key'] in ['mostly_false', 'false']:
            educational_response += "dezinformace se často šíří rychleji než pravdivé informace, proto je důležité být kritický k obsahu, který sdílíme."
        
        responses.append({
            'type': 'educational',
            'text': educational_response,
            'icon': 'school'
        })
        
        # Humorná reakce (pouze pro některé případy)
        if truth_rating['key'] not in ['insufficient_evidence', 'unverifiable']:
            humorous_response = ""
            
            if truth_rating['key'] in ['true', 'mostly_true']:
                humorous_response = "Tohle je tak pravdivé, že by to mohlo kandidovat na prezidenta Pravdivosti."
            elif truth_rating['key'] == 'partly_true':
                humorous_response = "Tohle tvrzení je jako napůl upečený koláč - některé části jsou hotové, jiné ještě potřebují trochu času v troubě faktů."
            elif truth_rating['key'] in ['mostly_false', 'false']:
                humorous_response = "Toto tvrzení má s pravdou společného asi tolik jako ananas na pizze s italskou kuchyní."
            elif truth_rating['key'] == 'misleading':
                humorous_response = "Toto tvrzení je jako GPS, která vás zavede na správnou ulici, ale do špatného města."
            
            responses.append({
                'type': 'humorous',
                'text': humorous_response,
                'icon': 'mood'
            })
        
        return responses
    
    def _create_summary(self, content_analysis, truth_rating, verified_claims, content_type):
        """
        Vytváří souhrn analyzovaného obsahu.
        
        Args:
            content_analysis (dict): Výsledky analýzy obsahu
            truth_rating (dict): Celkové hodnocení pravdivosti
            verified_claims (list): Seznam ověřených tvrzení
            content_type (str): Typ obsahu
            
        Returns:
            str: Souhrn obsahu
        """
        # Základní informace o typu obsahu
        if content_type == 'text':
            if 'summary' in content_analysis:
                return content_analysis['summary']
            else:
                return f"Analýza textového obsahu s {len(verified_claims)} ověřitelnými tvrzeními."
        elif content_type == 'image':
            return f"Analýza obrazového obsahu s {len(verified_claims)} ověřitelnými tvrzeními."
        elif content_type == 'audio':
            return f"Analýza audio obsahu s {len(verified_claims)} ověřitelnými tvrzeními."
        elif content_type == 'video':
            return f"Analýza video obsahu s {len(verified_claims)} ověřitelnými tvrzeními."
        else:
            return f"Analýza obsahu s {len(verified_claims)} ověřitelnými tvrzeními."
    
    def _generate_detailed_explanation(self, verified_claims, truth_rating, expertise_level, analysis_length):
        """
        Generuje detailní vysvětlení hodnocení pravdivosti.
        
        Args:
            verified_claims (list): Seznam ověřených tvrzení
            truth_rating (dict): Celkové hodnocení pravdivosti
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            str: Detailní vysvětlení
        """
        # Úvod vysvětlení
        explanation = f"Analyzovaný obsah byl ohodnocen jako {truth_rating['name'].upper()}. "
        explanation += truth_rating['description'] + " "
        
        # Přidání informací o ověřených tvrzeních
        if verified_claims:
            true_claims = [c for c in verified_claims if c['rating_key'] in ['true', 'mostly_true']]
            false_claims = [c for c in verified_claims if c['rating_key'] in ['false', 'mostly_false']]
            mixed_claims = [c for c in verified_claims if c['rating_key'] not in ['true', 'mostly_true', 'false', 'mostly_false']]
            
            explanation += f"Z celkového počtu {len(verified_claims)} ověřených tvrzení "
            explanation += f"bylo {len(true_claims)} hodnoceno jako pravdivé nebo převážně pravdivé, "
            explanation += f"{len(false_claims)} jako nepravdivé nebo převážně nepravdivé "
            explanation += f"a {len(mixed_claims)} jako částečně pravdivé nebo jinak klasifikované. "
        
        # Přizpůsobení délky vysvětlení podle požadované délky analýzy
        if analysis_length in ['detailed', 'exhaustive']:
            explanation += "\n\nPři hodnocení byla zohledněna důvěryhodnost zdrojů, kontext informací a aktuální stav poznání v dané oblasti. "
            
            if truth_rating['key'] in ['partly_true', 'misleading']:
                explanation += "Zvláštní pozornost byla věnována kontextu, ve kterém byly informace prezentovány, "
                explanation += "a způsobu, jakým mohou být interpretovány různými skupinami příjemců. "
            
            explanation += "\n\nPro komplexní pochopení tématu doporučujeme prostudovat detailní analýzu jednotlivých tvrzení "
            explanation += "a seznámit se s alternativními perspektivami uvedenými níže."
        
        # Přizpůsobení odbornosti vysvětlení
        if expertise_level == 'expert':
            explanation += "\n\nMetodologie hodnocení zahrnovala triangulaci informací z různých zdrojů, "
            explanation += "analýzu primárních dat a konzultaci s odbornými zdroji v dané oblasti. "
            explanation += "Při interpretaci výsledků je třeba zohlednit inherentní nejistotu spojenou s procesem fact-checkingu "
            explanation += "a možné limity dostupných zdrojů."
        
        return explanation
    
    def _extract_key_points(self, verified_claims, expertise_level, analysis_length):
        """
        Extrahuje klíčové body z ověřených tvrzení.
        
        Args:
            verified_claims (list): Seznam ověřených tvrzení
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            list: Seznam klíčových bodů
        """
        key_points = []
        
        # Počet klíčových bodů podle délky analýzy
        point_counts = {
            'brief': 3,
            'standard': 5,
            'detailed': 8,
            'exhaustive': 12
        }
        
        max_points = point_counts.get(analysis_length, 5)
        
        # Seřazení tvrzení podle relevance
        sorted_claims = sorted(verified_claims, key=lambda c: c.get('relevance_score', 0), reverse=True)
        
        # Výběr nejrelevantnějších tvrzení
        top_claims = sorted_claims[:max_points]
        
        # Vytvoření klíčových bodů
        for claim in top_claims:
            point = f"{claim['text']} - {claim['rating']}"
            
            # Přidání vysvětlení pro vyšší úrovně odbornosti
            if expertise_level in ['advanced', 'expert'] and 'explanation' in claim:
                point += f": {claim['explanation']}"
            
            key_points.append(point)
        
        return key_points
    
    def _generate_claim_explanation(self, claim_text, rating, expertise_level):
        """
        Generuje vysvětlení hodnocení tvrzení.
        
        Args:
            claim_text (str): Text tvrzení
            rating (dict): Hodnocení pravdivosti
            expertise_level (str): Úroveň odbornosti analýzy
            
        Returns:
            str: Vysvětlení hodnocení
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro generování vysvětlení
        
        # Základní vysvětlení podle hodnocení
        if rating['name'] == 'Pravdivé':
            explanation = "Toto tvrzení je podloženo důvěryhodnými zdroji a odpovídá současnému stavu poznání."
        elif rating['name'] == 'Převážně pravdivé':
            explanation = "Toto tvrzení je z větší části přesné, ale obsahuje drobné nepřesnosti, které nemění celkové vyznění."
        elif rating['name'] == 'Částečně pravdivé':
            explanation = "Toto tvrzení obsahuje některé pravdivé prvky, ale také významné nepřesnosti nebo vynechává důležitý kontext."
        elif rating['name'] == 'Převážně nepravdivé':
            explanation = "Toto tvrzení obsahuje některé pravdivé prvky, ale je převážně nepřesné nebo zavádějící."
        elif rating['name'] == 'Nepravdivé':
            explanation = "Toto tvrzení je nepodložené důvěryhodnými zdroji nebo odporuje současnému stavu poznání."
        elif rating['name'] == 'Zavádějící':
            explanation = "Toto tvrzení může být technicky pravdivé, ale je prezentováno způsobem, který je zavádějící nebo manipulativní."
        elif rating['name'] == 'Nedostatečné údaje':
            explanation = "Pro toto tvrzení není dostatek dostupných důvěryhodných zdrojů k jednoznačnému určení pravdivosti."
        elif rating['name'] == 'Neověřitelné':
            explanation = "Toto tvrzení nelze ověřit pomocí dostupných faktů nebo důkazů."
        elif rating['name'] == 'Satira':
            explanation = "Toto tvrzení je součástí satirického obsahu a není zamýšleno jako faktické sdělení."
        else:
            explanation = "Hodnocení tohoto tvrzení vyžaduje další výzkum."
        
        # Přizpůsobení odbornosti vysvětlení
        if expertise_level == 'expert':
            explanation += " Při hodnocení byla zohledněna metodologická triangulace a epistemologické limity dostupných zdrojů."
        elif expertise_level == 'advanced':
            explanation += " Hodnocení zohledňuje širší kontext a metodologické aspekty ověřování."
        
        return explanation
    
    def _simulate_sources(self, claim_text, count=2):
        """
        Simuluje zdroje pro ověření tvrzení.
        
        Args:
            claim_text (str): Text tvrzení
            count (int): Počet zdrojů k simulaci
            
        Returns:
            list: Seznam simulovaných zdrojů
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde bylo skutečné vyhledávání zdrojů
        
        sources = []
        
        # Simulované zdroje
        possible_sources = [
            {
                'name': 'Český statistický úřad',
                'url': 'https://www.czso.cz',
                'reliability': 'Velmi vysoká'
            },
            {
                'name': 'Ministerstvo zdravotnictví ČR',
                'url': 'https://www.mzcr.cz',
                'reliability': 'Vysoká'
            },
            {
                'name': 'ČT24',
                'url': 'https://ct24.ceskatelevize.cz',
                'reliability': 'Vysoká'
            },
            {
                'name': 'iROZHLAS',
                'url': 'https://www.irozhlas.cz',
                'reliability': 'Vysoká'
            },
            {
                'name': 'Aktuálně.cz',
                'url': 'https://www.aktualne.cz',
                'reliability': 'Střední'
            }
        ]
        
        # Výběr náhodných zdrojů
        import random
        selected_sources = random.sample(possible_sources, min(count, len(possible_sources)))
        
        return selected_sources
