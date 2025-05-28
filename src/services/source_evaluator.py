"""
Source Evaluator Module
-------------------
Modul pro hodnocení důvěryhodnosti zdrojů a jejich validaci pro fact-checking.
"""

import logging
import re
import requests
from urllib.parse import urlparse
import json
import datetime
import time
from bs4 import BeautifulSoup
import numpy as np

# Konfigurace logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SourceEvaluator:
    """
    Třída pro hodnocení důvěryhodnosti zdrojů a jejich validaci pro fact-checking.
    """
    
    def __init__(self):
        """Inicializace evaluátoru zdrojů."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("SourceEvaluator inicializován")
        
        # Načtení databáze důvěryhodných zdrojů
        self.trusted_sources_db = self._load_trusted_sources_db()
        
        # Načtení databáze problematických zdrojů
        self.problematic_sources_db = self._load_problematic_sources_db()
        
        # Váhy pro jednotlivé faktory hodnocení
        self.evaluation_weights = {
            'expertise': 0.20,
            'transparency': 0.15,
            'past_accuracy': 0.20,
            'editorial_process': 0.15,
            'independence': 0.15,
            'recency': 0.10,
            'citation_quality': 0.05
        }
    
    def evaluate_source(self, source_url, claim_text=None, expertise_level='medium'):
        """
        Hodnotí důvěryhodnost zdroje na základě různých faktorů.
        
        Args:
            source_url (str): URL zdroje k hodnocení
            claim_text (str, optional): Text tvrzení, pro které je zdroj hodnocen
            expertise_level (str): Úroveň odbornosti hodnocení ('basic', 'medium', 'advanced', 'expert')
            
        Returns:
            dict: Výsledky hodnocení zdroje
        """
        self.logger.info(f"Začínám hodnocení zdroje: {source_url}")
        
        try:
            # Validace URL
            if not self._is_valid_url(source_url):
                return {
                    'error': 'Neplatná URL adresa',
                    'reliability_score': 0.0,
                    'reliability_level': 'Nehodnoceno',
                    'evaluation_factors': {}
                }
            
            # Extrakce domény
            domain = self._extract_domain(source_url)
            
            # Kontrola v databázi důvěryhodných zdrojů
            trusted_source_info = self._check_trusted_sources_db(domain)
            
            # Kontrola v databázi problematických zdrojů
            problematic_source_info = self._check_problematic_sources_db(domain)
            
            # Získání metadat stránky
            page_metadata = self._fetch_page_metadata(source_url)
            
            # Hodnocení jednotlivých faktorů
            evaluation_factors = {}
            
            # 1. Odbornost a kvalifikace
            expertise_score = self._evaluate_expertise(domain, page_metadata, trusted_source_info)
            evaluation_factors['expertise'] = {
                'score': expertise_score,
                'description': self._get_expertise_description(expertise_score)
            }
            
            # 2. Transparentnost
            transparency_score = self._evaluate_transparency(domain, page_metadata, trusted_source_info)
            evaluation_factors['transparency'] = {
                'score': transparency_score,
                'description': self._get_transparency_description(transparency_score)
            }
            
            # 3. Přesnost v minulosti
            past_accuracy_score = self._evaluate_past_accuracy(domain, trusted_source_info, problematic_source_info)
            evaluation_factors['past_accuracy'] = {
                'score': past_accuracy_score,
                'description': self._get_past_accuracy_description(past_accuracy_score)
            }
            
            # 4. Redakční proces
            editorial_process_score = self._evaluate_editorial_process(domain, page_metadata, trusted_source_info)
            evaluation_factors['editorial_process'] = {
                'score': editorial_process_score,
                'description': self._get_editorial_process_description(editorial_process_score)
            }
            
            # 5. Nezávislost
            independence_score = self._evaluate_independence(domain, page_metadata, trusted_source_info, problematic_source_info)
            evaluation_factors['independence'] = {
                'score': independence_score,
                'description': self._get_independence_description(independence_score)
            }
            
            # 6. Aktuálnost
            recency_score = self._evaluate_recency(page_metadata)
            evaluation_factors['recency'] = {
                'score': recency_score,
                'description': self._get_recency_description(recency_score)
            }
            
            # 7. Kvalita citací
            citation_quality_score = self._evaluate_citation_quality(page_metadata)
            evaluation_factors['citation_quality'] = {
                'score': citation_quality_score,
                'description': self._get_citation_quality_description(citation_quality_score)
            }
            
            # Výpočet celkového skóre důvěryhodnosti
            reliability_score = self._calculate_reliability_score(evaluation_factors)
            
            # Určení úrovně důvěryhodnosti
            reliability_level = self._determine_reliability_level(reliability_score)
            
            # Příprava výstupu
            result = {
                'url': source_url,
                'domain': domain,
                'reliability_score': reliability_score,
                'reliability_level': reliability_level,
                'evaluation_factors': evaluation_factors,
                'source_type': self._determine_source_type(domain, page_metadata),
                'source_info': {
                    'name': page_metadata.get('site_name', domain),
                    'description': page_metadata.get('description', ''),
                    'is_trusted': trusted_source_info is not None,
                    'is_problematic': problematic_source_info is not None
                }
            }
            
            # Přidání informací o důvěryhodném zdroji, pokud je k dispozici
            if trusted_source_info:
                result['source_info']['trusted_info'] = trusted_source_info
            
            # Přidání informací o problematickém zdroji, pokud je k dispozici
            if problematic_source_info:
                result['source_info']['problematic_info'] = problematic_source_info
            
            # Přizpůsobení výstupu podle úrovně odbornosti
            result = self._adapt_output_to_expertise_level(result, expertise_level)
            
            self.logger.info(f"Hodnocení zdroje dokončeno: {domain}, skóre: {reliability_score:.2f}, úroveň: {reliability_level}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chyba při hodnocení zdroje: {str(e)}", exc_info=True)
            return {
                'error': f'Chyba při hodnocení zdroje: {str(e)}',
                'reliability_score': 0.0,
                'reliability_level': 'Nehodnoceno',
                'evaluation_factors': {}
            }
    
    def evaluate_multiple_sources(self, sources, claim_text=None, expertise_level='medium'):
        """
        Hodnotí důvěryhodnost více zdrojů a poskytuje souhrnné hodnocení.
        
        Args:
            sources (list): Seznam URL zdrojů k hodnocení
            claim_text (str, optional): Text tvrzení, pro které jsou zdroje hodnoceny
            expertise_level (str): Úroveň odbornosti hodnocení
            
        Returns:
            dict: Výsledky hodnocení zdrojů včetně souhrnného hodnocení
        """
        self.logger.info(f"Začínám hodnocení {len(sources)} zdrojů")
        
        source_evaluations = []
        
        # Hodnocení jednotlivých zdrojů
        for source_url in sources:
            evaluation = self.evaluate_source(source_url, claim_text, expertise_level)
            source_evaluations.append(evaluation)
        
        # Výpočet průměrného skóre důvěryhodnosti
        valid_scores = [e['reliability_score'] for e in source_evaluations if 'error' not in e]
        avg_reliability_score = np.mean(valid_scores) if valid_scores else 0.0
        
        # Určení souhrnné úrovně důvěryhodnosti
        overall_reliability_level = self._determine_reliability_level(avg_reliability_score)
        
        # Příprava souhrnného výstupu
        result = {
            'sources': source_evaluations,
            'overall_reliability_score': avg_reliability_score,
            'overall_reliability_level': overall_reliability_level,
            'source_count': len(sources),
            'valid_source_count': len(valid_scores),
            'source_types_distribution': self._calculate_source_types_distribution(source_evaluations)
        }
        
        self.logger.info(f"Hodnocení zdrojů dokončeno, průměrné skóre: {avg_reliability_score:.2f}, úroveň: {overall_reliability_level}")
        return result
    
    def find_additional_sources(self, claim_text, existing_sources=None, min_reliability_score=0.6, max_sources=5):
        """
        Hledá další důvěryhodné zdroje pro ověření tvrzení.
        
        Args:
            claim_text (str): Text tvrzení k ověření
            existing_sources (list, optional): Seznam již použitých URL zdrojů
            min_reliability_score (float): Minimální požadované skóre důvěryhodnosti
            max_sources (int): Maximální počet zdrojů k nalezení
            
        Returns:
            list: Seznam nalezených důvěryhodných zdrojů
        """
        self.logger.info(f"Hledám další zdroje pro tvrzení: {claim_text[:50]}...")
        
        # Toto je zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro vyhledávání relevantních zdrojů
        
        # Pro demonstrační účely vracíme simulované výsledky
        additional_sources = [
            {
                'url': 'https://www.example.com/fact-check-1',
                'title': 'Fact Check: Analýza tvrzení o klimatických změnách',
                'snippet': 'Podrobná analýza tvrzení o klimatických změnách a jejich dopadech...',
                'reliability_score': 0.85,
                'reliability_level': 'Vysoká důvěryhodnost'
            },
            {
                'url': 'https://www.example.org/research-paper',
                'title': 'Výzkumná studie: Dopady klimatických změn',
                'snippet': 'Vědecká studie zkoumající dopady klimatických změn na ekosystémy...',
                'reliability_score': 0.92,
                'reliability_level': 'Velmi vysoká důvěryhodnost'
            }
        ]
        
        return additional_sources
    
    def _is_valid_url(self, url):
        """
        Kontroluje, zda je URL platná.
        
        Args:
            url (str): URL k validaci
            
        Returns:
            bool: True, pokud je URL platná, jinak False
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_domain(self, url):
        """
        Extrahuje doménu z URL.
        
        Args:
            url (str): URL, ze které se má extrahovat doména
            
        Returns:
            str: Extrahovaná doména
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Odstranění 'www.' z domény
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return url
    
    def _load_trusted_sources_db(self):
        """
        Načte databázi důvěryhodných zdrojů.
        
        Returns:
            dict: Databáze důvěryhodných zdrojů
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde bylo načítání z databáze
        
        trusted_sources = {
            # Zpravodajské zdroje
            'ct24.ceskatelevize.cz': {
                'name': 'ČT24',
                'type': 'news',
                'reliability': 0.85,
                'expertise': 0.80,
                'transparency': 0.90,
                'independence': 0.85,
                'editorial_process': 0.90,
                'description': 'Zpravodajský kanál České televize, veřejnoprávní médium.'
            },
            'irozhlas.cz': {
                'name': 'iROZHLAS',
                'type': 'news',
                'reliability': 0.85,
                'expertise': 0.80,
                'transparency': 0.90,
                'independence': 0.85,
                'editorial_process': 0.90,
                'description': 'Zpravodajský server Českého rozhlasu, veřejnoprávní médium.'
            },
            'denik.cz': {
                'name': 'Deník',
                'type': 'news',
                'reliability': 0.75,
                'expertise': 0.70,
                'transparency': 0.75,
                'independence': 0.70,
                'editorial_process': 0.75,
                'description': 'Zpravodajský server vydavatelství Vltava Labe Media.'
            },
            'idnes.cz': {
                'name': 'iDNES',
                'type': 'news',
                'reliability': 0.70,
                'expertise': 0.75,
                'transparency': 0.70,
                'independence': 0.60,
                'editorial_process': 0.75,
                'description': 'Zpravodajský server vydavatelství MAFRA.'
            },
            'aktualne.cz': {
                'name': 'Aktuálně.cz',
                'type': 'news',
                'reliability': 0.80,
                'expertise': 0.75,
                'transparency': 0.80,
                'independence': 0.75,
                'editorial_process': 0.80,
                'description': 'Zpravodajský server vydavatelství Economia.'
            },
            'seznamzpravy.cz': {
                'name': 'Seznam Zprávy',
                'type': 'news',
                'reliability': 0.75,
                'expertise': 0.70,
                'transparency': 0.75,
                'independence': 0.70,
                'editorial_process': 0.75,
                'description': 'Zpravodajský server společnosti Seznam.cz.'
            },
            
            # Vědecké a akademické zdroje
            'vedavyzkum.cz': {
                'name': 'Vědavýzkum.cz',
                'type': 'academic',
                'reliability': 0.90,
                'expertise': 0.95,
                'transparency': 0.85,
                'independence': 0.90,
                'editorial_process': 0.85,
                'description': 'Portál o vědě a výzkumu v České republice.'
            },
            'osel.cz': {
                'name': 'OSEL.cz',
                'type': 'academic',
                'reliability': 0.85,
                'expertise': 0.90,
                'transparency': 0.80,
                'independence': 0.85,
                'editorial_process': 0.80,
                'description': 'Objective Source E-Learning - portál o vědě a technice.'
            },
            'sciencemag.org': {
                'name': 'Science',
                'type': 'academic',
                'reliability': 0.95,
                'expertise': 0.98,
                'transparency': 0.90,
                'independence': 0.90,
                'editorial_process': 0.95,
                'description': 'Prestižní vědecký časopis vydávaný American Association for the Advancement of Science.'
            },
            'nature.com': {
                'name': 'Nature',
                'type': 'academic',
                'reliability': 0.95,
                'expertise': 0.98,
                'transparency': 0.90,
                'independence': 0.90,
                'editorial_process': 0.95,
                'description': 'Prestižní vědecký časopis vydávaný Springer Nature.'
            },
            
            # Vládní a oficiální zdroje
            'mzcr.cz': {
                'name': 'Ministerstvo zdravotnictví ČR',
                'type': 'government',
                'reliability': 0.90,
                'expertise': 0.85,
                'transparency': 0.80,
                'independence': 0.70,
                'editorial_process': 0.85,
                'description': 'Oficiální web Ministerstva zdravotnictví České republiky.'
            },
            'czso.cz': {
                'name': 'Český statistický úřad',
                'type': 'government',
                'reliability': 0.95,
                'expertise': 0.90,
                'transparency': 0.85,
                'independence': 0.85,
                'editorial_process': 0.90,
                'description': 'Oficiální web Českého statistického úřadu.'
            },
            'europa.eu': {
                'name': 'Evropská unie',
                'type': 'government',
                'reliability': 0.90,
                'expertise': 0.85,
                'transparency': 0.80,
                'independence': 0.75,
                'editorial_process': 0.85,
                'description': 'Oficiální web Evropské unie.'
            },
            
            # Fact-checking organizace
            'demagog.cz': {
                'name': 'Demagog.cz',
                'type': 'fact_checking',
                'reliability': 0.85,
                'expertise': 0.80,
                'transparency': 0.90,
                'independence': 0.85,
                'editorial_process': 0.85,
                'description': 'Český fact-checkingový projekt zaměřený na ověřování výroků politiků.'
            },
            'factcheck.org': {
                'name': 'FactCheck.org',
                'type': 'fact_checking',
                'reliability': 0.90,
                'expertise': 0.85,
                'transparency': 0.90,
                'independence': 0.85,
                'editorial_process': 0.90,
                'description': 'Americký fact-checkingový projekt Annenberg Public Policy Center.'
            },
            'snopes.com': {
                'name': 'Snopes',
                'type': 'fact_checking',
                'reliability': 0.85,
                'expertise': 0.80,
                'transparency': 0.85,
                'independence': 0.80,
                'editorial_process': 0.85,
                'description': 'Jeden z nejstarších fact-checkingových webů na internetu.'
            }
        }
        
        return trusted_sources
    
    def _load_problematic_sources_db(self):
        """
        Načte databázi problematických zdrojů.
        
        Returns:
            dict: Databáze problematických zdrojů
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde bylo načítání z databáze
        
        problematic_sources = {
            'example-fake-news.com': {
                'name': 'Example Fake News',
                'type': 'fake_news',
                'issues': ['Šíření dezinformací', 'Nedostatek transparentnosti', 'Žádný redakční proces'],
                'reliability': 0.10,
                'description': 'Známý zdroj dezinformací a falešných zpráv.'
            },
            'conspiracy-theories.org': {
                'name': 'Conspiracy Theories',
                'type': 'conspiracy',
                'issues': ['Šíření konspiračních teorií', 'Nedostatek důkazů', 'Manipulativní obsah'],
                'reliability': 0.15,
                'description': 'Web zaměřený na konspirační teorie bez faktických podkladů.'
            }
        }
        
        return problematic_sources
    
    def _check_trusted_sources_db(self, domain):
        """
        Kontroluje, zda je doména v databázi důvěryhodných zdrojů.
        
        Args:
            domain (str): Doména ke kontrole
            
        Returns:
            dict: Informace o důvěryhodném zdroji nebo None
        """
        return self.trusted_sources_db.get(domain)
    
    def _check_problematic_sources_db(self, domain):
        """
        Kontroluje, zda je doména v databázi problematických zdrojů.
        
        Args:
            domain (str): Doména ke kontrole
            
        Returns:
            dict: Informace o problematickém zdroji nebo None
        """
        return self.problematic_sources_db.get(domain)
    
    def _fetch_page_metadata(self, url):
        """
        Získává metadata webové stránky.
        
        Args:
            url (str): URL stránky
            
        Returns:
            dict: Metadata stránky
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde bylo skutečné načítání stránky
        # a extrakce metadat
        
        metadata = {
            'title': 'Příklad titulku stránky',
            'description': 'Příklad popisu stránky',
            'site_name': 'Příklad názvu webu',
            'author': 'Příklad autora',
            'published_date': '2023-01-01',
            'modified_date': '2023-01-02',
            'keywords': ['příklad', 'klíčová slova'],
            'has_citations': True,
            'has_author_info': True,
            'has_about_page': True,
            'has_contact_info': True,
            'has_privacy_policy': True,
            'has_terms_of_service': True,
            'has_funding_info': True
        }
        
        return metadata
    
    def _evaluate_expertise(self, domain, page_metadata, trusted_source_info):
        """
        Hodnotí odbornost a kvalifikaci zdroje.
        
        Args:
            domain (str): Doména zdroje
            page_metadata (dict): Metadata stránky
            trusted_source_info (dict): Informace o důvěryhodném zdroji
            
        Returns:
            float: Skóre odbornosti (0.0 - 1.0)
        """
        # Pokud je zdroj v databázi důvěryhodných zdrojů, použijeme jeho hodnocení
        if trusted_source_info and 'expertise' in trusted_source_info:
            return trusted_source_info['expertise']
        
        # Jinak provedeme vlastní hodnocení
        score = 0.5  # Výchozí hodnota
        
        # Kontrola přítomnosti informací o autorovi
        if page_metadata.get('has_author_info', False):
            score += 0.1
        
        # Kontrola typu domény
        if domain.endswith('.edu') or domain.endswith('.gov') or domain.endswith('.ac.uk'):
            score += 0.2
        elif domain.endswith('.org'):
            score += 0.1
        
        # Omezení skóre na rozsah 0.0 - 1.0
        return max(0.0, min(1.0, score))
    
    def _evaluate_transparency(self, domain, page_metadata, trusted_source_info):
        """
        Hodnotí transparentnost zdroje.
        
        Args:
            domain (str): Doména zdroje
            page_metadata (dict): Metadata stránky
            trusted_source_info (dict): Informace o důvěryhodném zdroji
            
        Returns:
            float: Skóre transparentnosti (0.0 - 1.0)
        """
        # Pokud je zdroj v databázi důvěryhodných zdrojů, použijeme jeho hodnocení
        if trusted_source_info and 'transparency' in trusted_source_info:
            return trusted_source_info['transparency']
        
        # Jinak provedeme vlastní hodnocení
        score = 0.5  # Výchozí hodnota
        
        # Kontrola přítomnosti stránky "O nás"
        if page_metadata.get('has_about_page', False):
            score += 0.1
        
        # Kontrola přítomnosti kontaktních informací
        if page_metadata.get('has_contact_info', False):
            score += 0.1
        
        # Kontrola přítomnosti informací o financování
        if page_metadata.get('has_funding_info', False):
            score += 0.2
        
        # Kontrola přítomnosti zásad ochrany soukromí a podmínek služby
        if page_metadata.get('has_privacy_policy', False) and page_metadata.get('has_terms_of_service', False):
            score += 0.1
        
        # Omezení skóre na rozsah 0.0 - 1.0
        return max(0.0, min(1.0, score))
    
    def _evaluate_past_accuracy(self, domain, trusted_source_info, problematic_source_info):
        """
        Hodnotí přesnost zdroje v minulosti.
        
        Args:
            domain (str): Doména zdroje
            trusted_source_info (dict): Informace o důvěryhodném zdroji
            problematic_source_info (dict): Informace o problematickém zdroji
            
        Returns:
            float: Skóre přesnosti v minulosti (0.0 - 1.0)
        """
        # Pokud je zdroj v databázi problematických zdrojů, má nízké skóre
        if problematic_source_info:
            return problematic_source_info.get('reliability', 0.1)
        
        # Pokud je zdroj v databázi důvěryhodných zdrojů, použijeme jeho hodnocení
        if trusted_source_info and 'reliability' in trusted_source_info:
            return trusted_source_info['reliability']
        
        # Jinak použijeme výchozí hodnotu
        return 0.5
    
    def _evaluate_editorial_process(self, domain, page_metadata, trusted_source_info):
        """
        Hodnotí redakční proces zdroje.
        
        Args:
            domain (str): Doména zdroje
            page_metadata (dict): Metadata stránky
            trusted_source_info (dict): Informace o důvěryhodném zdroji
            
        Returns:
            float: Skóre redakčního procesu (0.0 - 1.0)
        """
        # Pokud je zdroj v databázi důvěryhodných zdrojů, použijeme jeho hodnocení
        if trusted_source_info and 'editorial_process' in trusted_source_info:
            return trusted_source_info['editorial_process']
        
        # Jinak provedeme vlastní hodnocení
        score = 0.5  # Výchozí hodnota
        
        # Kontrola typu domény (akademické a vládní zdroje mají obvykle dobrý redakční proces)
        if domain.endswith('.edu') or domain.endswith('.gov') or domain.endswith('.ac.uk'):
            score += 0.2
        
        # Kontrola přítomnosti informací o autorovi
        if page_metadata.get('has_author_info', False):
            score += 0.1
        
        # Omezení skóre na rozsah 0.0 - 1.0
        return max(0.0, min(1.0, score))
    
    def _evaluate_independence(self, domain, page_metadata, trusted_source_info, problematic_source_info):
        """
        Hodnotí nezávislost zdroje.
        
        Args:
            domain (str): Doména zdroje
            page_metadata (dict): Metadata stránky
            trusted_source_info (dict): Informace o důvěryhodném zdroji
            problematic_source_info (dict): Informace o problematickém zdroji
            
        Returns:
            float: Skóre nezávislosti (0.0 - 1.0)
        """
        # Pokud je zdroj v databázi problematických zdrojů, má nízké skóre
        if problematic_source_info:
            return 0.2
        
        # Pokud je zdroj v databázi důvěryhodných zdrojů, použijeme jeho hodnocení
        if trusted_source_info and 'independence' in trusted_source_info:
            return trusted_source_info['independence']
        
        # Jinak provedeme vlastní hodnocení
        score = 0.5  # Výchozí hodnota
        
        # Kontrola přítomnosti informací o financování
        if page_metadata.get('has_funding_info', False):
            score += 0.2
        
        # Kontrola typu domény (vládní zdroje mohou mít nižší nezávislost)
        if domain.endswith('.gov'):
            score -= 0.1
        
        # Omezení skóre na rozsah 0.0 - 1.0
        return max(0.0, min(1.0, score))
    
    def _evaluate_recency(self, page_metadata):
        """
        Hodnotí aktuálnost informací.
        
        Args:
            page_metadata (dict): Metadata stránky
            
        Returns:
            float: Skóre aktuálnosti (0.0 - 1.0)
        """
        # Kontrola přítomnosti data publikace
        published_date = page_metadata.get('published_date')
        modified_date = page_metadata.get('modified_date')
        
        if not published_date and not modified_date:
            return 0.5  # Výchozí hodnota, pokud datum není k dispozici
        
        # Použití novějšího data
        date_str = modified_date if modified_date else published_date
        
        try:
            # Převod řetězce na datum
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Výpočet stáří v dnech
            age_days = (datetime.date.today() - date).days
            
            # Hodnocení podle stáří
            if age_days <= 7:  # Méně než týden
                return 1.0
            elif age_days <= 30:  # Méně než měsíc
                return 0.9
            elif age_days <= 90:  # Méně než čtvrt roku
                return 0.8
            elif age_days <= 365:  # Méně než rok
                return 0.7
            elif age_days <= 730:  # Méně než dva roky
                return 0.5
            elif age_days <= 1825:  # Méně než pět let
                return 0.3
            else:  # Více než pět let
                return 0.1
        except:
            return 0.5  # Výchozí hodnota v případě chyby
    
    def _evaluate_citation_quality(self, page_metadata):
        """
        Hodnotí kvalitu citací a odkazů.
        
        Args:
            page_metadata (dict): Metadata stránky
            
        Returns:
            float: Skóre kvality citací (0.0 - 1.0)
        """
        # Kontrola přítomnosti citací
        if page_metadata.get('has_citations', False):
            return 0.8
        else:
            return 0.4
    
    def _calculate_reliability_score(self, evaluation_factors):
        """
        Vypočítá celkové skóre důvěryhodnosti na základě jednotlivých faktorů.
        
        Args:
            evaluation_factors (dict): Hodnocení jednotlivých faktorů
            
        Returns:
            float: Celkové skóre důvěryhodnosti (0.0 - 1.0)
        """
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for factor, weight in self.evaluation_weights.items():
            if factor in evaluation_factors and 'score' in evaluation_factors[factor]:
                weighted_sum += evaluation_factors[factor]['score'] * weight
                weight_sum += weight
        
        # Pokud nejsou k dispozici žádné faktory, vrátíme výchozí hodnotu
        if weight_sum == 0:
            return 0.5
        
        # Výpočet váženého průměru
        return weighted_sum / weight_sum
    
    def _determine_reliability_level(self, reliability_score):
        """
        Určuje úroveň důvěryhodnosti na základě skóre.
        
        Args:
            reliability_score (float): Skóre důvěryhodnosti
            
        Returns:
            str: Úroveň důvěryhodnosti
        """
        if reliability_score >= 0.9:
            return "Velmi vysoká důvěryhodnost"
        elif reliability_score >= 0.75:
            return "Vysoká důvěryhodnost"
        elif reliability_score >= 0.6:
            return "Střední důvěryhodnost"
        elif reliability_score >= 0.4:
            return "Nízká důvěryhodnost"
        elif reliability_score >= 0.2:
            return "Velmi nízká důvěryhodnost"
        else:
            return "Nedůvěryhodný zdroj"
    
    def _determine_source_type(self, domain, page_metadata):
        """
        Určuje typ zdroje.
        
        Args:
            domain (str): Doména zdroje
            page_metadata (dict): Metadata stránky
            
        Returns:
            str: Typ zdroje
        """
        # Kontrola v databázi důvěryhodných zdrojů
        trusted_source_info = self._check_trusted_sources_db(domain)
        if trusted_source_info and 'type' in trusted_source_info:
            return trusted_source_info['type']
        
        # Jinak provedeme vlastní určení typu
        if domain.endswith('.gov'):
            return 'government'
        elif domain.endswith('.edu') or domain.endswith('.ac.uk'):
            return 'academic'
        elif domain.endswith('.org'):
            return 'organization'
        elif 'news' in domain or 'zpravy' in domain:
            return 'news'
        else:
            return 'other'
    
    def _adapt_output_to_expertise_level(self, result, expertise_level):
        """
        Přizpůsobuje výstup podle úrovně odbornosti.
        
        Args:
            result (dict): Výsledky hodnocení
            expertise_level (str): Úroveň odbornosti
            
        Returns:
            dict: Přizpůsobené výsledky hodnocení
        """
        if expertise_level == 'basic':
            # Pro základní úroveň zjednodušíme výstup
            simplified = {
                'url': result['url'],
                'domain': result['domain'],
                'reliability_level': result['reliability_level'],
                'source_type': self._get_source_type_description(result['source_type']),
                'source_name': result['source_info']['name']
            }
            return simplified
        elif expertise_level == 'expert':
            # Pro expertní úroveň přidáme detailní informace
            result['detailed_evaluation'] = self._get_detailed_evaluation(result)
            return result
        else:
            # Pro střední a pokročilou úroveň vrátíme standardní výstup
            return result
    
    def _get_source_type_description(self, source_type):
        """
        Vrací popis typu zdroje.
        
        Args:
            source_type (str): Typ zdroje
            
        Returns:
            str: Popis typu zdroje
        """
        descriptions = {
            'news': 'Zpravodajský zdroj',
            'academic': 'Akademický zdroj',
            'government': 'Vládní zdroj',
            'organization': 'Organizace',
            'fact_checking': 'Fact-checkingová organizace',
            'other': 'Ostatní zdroj'
        }
        
        return descriptions.get(source_type, 'Neznámý typ zdroje')
    
    def _get_detailed_evaluation(self, result):
        """
        Vytváří detailní hodnocení pro expertní úroveň.
        
        Args:
            result (dict): Výsledky hodnocení
            
        Returns:
            dict: Detailní hodnocení
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde bylo více detailů
        
        detailed = {
            'methodology': 'Hodnocení bylo provedeno na základě analýzy domény, metadat stránky a porovnání s databází důvěryhodných a problematických zdrojů.',
            'factor_weights': self.evaluation_weights,
            'confidence': 0.8,  # Míra jistoty hodnocení
            'limitations': 'Hodnocení je založeno na dostupných informacích a může se v čase měnit.'
        }
        
        return detailed
    
    def _get_expertise_description(self, score):
        """
        Vrací popis hodnocení odbornosti.
        
        Args:
            score (float): Skóre odbornosti
            
        Returns:
            str: Popis hodnocení odbornosti
        """
        if score >= 0.9:
            return "Zdroj má vynikající odbornost a kvalifikaci v dané oblasti."
        elif score >= 0.75:
            return "Zdroj má dobrou odbornost a kvalifikaci v dané oblasti."
        elif score >= 0.6:
            return "Zdroj má přiměřenou odbornost a kvalifikaci v dané oblasti."
        elif score >= 0.4:
            return "Zdroj má omezenou odbornost a kvalifikaci v dané oblasti."
        elif score >= 0.2:
            return "Zdroj má nízkou odbornost a kvalifikaci v dané oblasti."
        else:
            return "Zdroj nemá prokazatelnou odbornost a kvalifikaci v dané oblasti."
    
    def _get_transparency_description(self, score):
        """
        Vrací popis hodnocení transparentnosti.
        
        Args:
            score (float): Skóre transparentnosti
            
        Returns:
            str: Popis hodnocení transparentnosti
        """
        if score >= 0.9:
            return "Zdroj je vysoce transparentní ohledně své metodologie, financování a potenciálních konfliktů zájmů."
        elif score >= 0.75:
            return "Zdroj je transparentní ohledně své metodologie, financování a potenciálních konfliktů zájmů."
        elif score >= 0.6:
            return "Zdroj je částečně transparentní ohledně své metodologie, financování a potenciálních konfliktů zájmů."
        elif score >= 0.4:
            return "Zdroj má omezenou transparentnost ohledně své metodologie, financování a potenciálních konfliktů zájmů."
        elif score >= 0.2:
            return "Zdroj má nízkou transparentnost ohledně své metodologie, financování a potenciálních konfliktů zájmů."
        else:
            return "Zdroj není transparentní ohledně své metodologie, financování a potenciálních konfliktů zájmů."
    
    def _get_past_accuracy_description(self, score):
        """
        Vrací popis hodnocení přesnosti v minulosti.
        
        Args:
            score (float): Skóre přesnosti v minulosti
            
        Returns:
            str: Popis hodnocení přesnosti v minulosti
        """
        if score >= 0.9:
            return "Zdroj má vynikající historii přesnosti a spolehlivosti publikovaných informací."
        elif score >= 0.75:
            return "Zdroj má dobrou historii přesnosti a spolehlivosti publikovaných informací."
        elif score >= 0.6:
            return "Zdroj má přiměřenou historii přesnosti a spolehlivosti publikovaných informací."
        elif score >= 0.4:
            return "Zdroj má smíšenou historii přesnosti a spolehlivosti publikovaných informací."
        elif score >= 0.2:
            return "Zdroj má problematickou historii přesnosti a spolehlivosti publikovaných informací."
        else:
            return "Zdroj má velmi špatnou historii přesnosti a spolehlivosti publikovaných informací."
    
    def _get_editorial_process_description(self, score):
        """
        Vrací popis hodnocení redakčního procesu.
        
        Args:
            score (float): Skóre redakčního procesu
            
        Returns:
            str: Popis hodnocení redakčního procesu
        """
        if score >= 0.9:
            return "Zdroj má vynikající redakční proces a kontrolní mechanismy."
        elif score >= 0.75:
            return "Zdroj má dobrý redakční proces a kontrolní mechanismy."
        elif score >= 0.6:
            return "Zdroj má přiměřený redakční proces a kontrolní mechanismy."
        elif score >= 0.4:
            return "Zdroj má omezený redakční proces a kontrolní mechanismy."
        elif score >= 0.2:
            return "Zdroj má minimální redakční proces a kontrolní mechanismy."
        else:
            return "Zdroj nemá prokazatelný redakční proces a kontrolní mechanismy."
    
    def _get_independence_description(self, score):
        """
        Vrací popis hodnocení nezávislosti.
        
        Args:
            score (float): Skóre nezávislosti
            
        Returns:
            str: Popis hodnocení nezávislosti
        """
        if score >= 0.9:
            return "Zdroj je vysoce nezávislý bez významných politických, komerčních nebo jiných zájmů."
        elif score >= 0.75:
            return "Zdroj je nezávislý s minimálními politickými, komerčními nebo jinými zájmy."
        elif score >= 0.6:
            return "Zdroj je částečně nezávislý s některými politickými, komerčními nebo jinými zájmy."
        elif score >= 0.4:
            return "Zdroj má omezenou nezávislost s významnými politickými, komerčními nebo jinými zájmy."
        elif score >= 0.2:
            return "Zdroj má nízkou nezávislost s výraznými politickými, komerčními nebo jinými zájmy."
        else:
            return "Zdroj není nezávislý a je silně ovlivněn politickými, komerčními nebo jinými zájmy."
    
    def _get_recency_description(self, score):
        """
        Vrací popis hodnocení aktuálnosti.
        
        Args:
            score (float): Skóre aktuálnosti
            
        Returns:
            str: Popis hodnocení aktuálnosti
        """
        if score >= 0.9:
            return "Informace jsou velmi aktuální (méně než měsíc staré)."
        elif score >= 0.75:
            return "Informace jsou aktuální (méně než čtvrt roku staré)."
        elif score >= 0.6:
            return "Informace jsou relativně aktuální (méně než rok staré)."
        elif score >= 0.4:
            return "Informace jsou starší (1-2 roky)."
        elif score >= 0.2:
            return "Informace jsou zastaralé (2-5 let)."
        else:
            return "Informace jsou velmi zastaralé (více než 5 let)."
    
    def _get_citation_quality_description(self, score):
        """
        Vrací popis hodnocení kvality citací.
        
        Args:
            score (float): Skóre kvality citací
            
        Returns:
            str: Popis hodnocení kvality citací
        """
        if score >= 0.9:
            return "Zdroj má vynikající kvalitu citací a odkazů na další zdroje."
        elif score >= 0.75:
            return "Zdroj má dobrou kvalitu citací a odkazů na další zdroje."
        elif score >= 0.6:
            return "Zdroj má přiměřenou kvalitu citací a odkazů na další zdroje."
        elif score >= 0.4:
            return "Zdroj má omezenou kvalitu citací a odkazů na další zdroje."
        elif score >= 0.2:
            return "Zdroj má nízkou kvalitu citací a odkazů na další zdroje."
        else:
            return "Zdroj nemá žádné citace nebo odkazy na další zdroje."
    
    def _calculate_source_types_distribution(self, source_evaluations):
        """
        Vypočítá distribuci typů zdrojů.
        
        Args:
            source_evaluations (list): Seznam hodnocení zdrojů
            
        Returns:
            dict: Distribuce typů zdrojů
        """
        distribution = {}
        
        for evaluation in source_evaluations:
            if 'error' in evaluation:
                continue
                
            source_type = evaluation.get('source_type', 'unknown')
            distribution[source_type] = distribution.get(source_type, 0) + 1
        
        return distribution
