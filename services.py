"""
Služba pro integraci s OpenAI API.

Tento modul poskytuje služby pro komunikaci s OpenAI API a analýzu tvrzení.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

class OpenAIService:
    """
    Služba pro komunikaci s OpenAI API.
    """
    
    def __init__(self, api_key: str):
        """
        Inicializace služby.
        
        Args:
            api_key: OpenAI API klíč
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def analyze_claim(self, claim_text: str, analysis_type: str = 'standard') -> Dict[str, Any]:
        """
        Analyzuje tvrzení pomocí OpenAI API.
        
        Args:
            claim_text: Text tvrzení k analýze
            analysis_type: Typ analýzy (standard, quick, detailed)
            
        Returns:
            Výsledek analýzy jako slovník
        """
        # Výběr správného promptu podle typu analýzy
        prompt = self._get_prompt_for_analysis_type(analysis_type)
        
        # Sestavení zprávy pro API
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": claim_text}
        ]
        
        # Nastavení parametrů požadavku
        data = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1000,
            "response_format": {"type": "json_object"}
        }
        
        try:
            # Odeslání požadavku na API
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            
            # Zpracování odpovědi
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parsování JSON odpovědi
            analysis_result = json.loads(content)
            
            # Přidání typu analýzy do výsledku
            analysis_result["analysis_type"] = analysis_type
            
            return analysis_result
        
        except requests.exceptions.RequestException as e:
            # Ošetření chyb při komunikaci s API
            print(f"Chyba při komunikaci s OpenAI API: {str(e)}")
            return self._get_error_response(str(e))
        
        except json.JSONDecodeError as e:
            # Ošetření chyb při parsování JSON
            print(f"Chyba při parsování odpovědi: {str(e)}")
            return self._get_error_response("Neplatná odpověď od API")
        
        except Exception as e:
            # Ošetření ostatních chyb
            print(f"Neočekávaná chyba: {str(e)}")
            return self._get_error_response("Neočekávaná chyba při analýze")
    
    def _get_prompt_for_analysis_type(self, analysis_type: str) -> str:
        """
        Vrátí prompt pro daný typ analýzy.
        
        Args:
            analysis_type: Typ analýzy (standard, quick, detailed)
            
        Returns:
            Prompt pro OpenAI API
        """
        prompts = {
            'quick': """
                Jsi expertní fact-checker, který analyzuje tvrzení a určuje jejich pravdivost.
                Proveď rychlou analýzu následujícího tvrzení a vrať výsledek v JSON formátu s těmito poli:
                - verdict: Verdikt o pravdivosti (pravdivé, částečně pravdivé, nepravdivé, zavádějící, nelze ověřit)
                - confidence: Míra jistoty verdiktu v procentech (0-100)
                - explanation: Stručné vysvětlení verdiktu (max. 2 věty)
                
                Odpověz pouze v JSON formátu bez dalšího textu.
            """,
            
            'standard': """
                Jsi expertní fact-checker, který analyzuje tvrzení a určuje jejich pravdivost.
                Proveď důkladnou analýzu následujícího tvrzení a vrať výsledek v JSON formátu s těmito poli:
                - verdict: Verdikt o pravdivosti (pravdivé, částečně pravdivé, nepravdivé, zavádějící, nelze ověřit)
                - confidence: Míra jistoty verdiktu v procentech (0-100)
                - explanation: Vysvětlení verdiktu (3-5 vět)
                - evidences: Seznam důkazů podporujících verdikt (pole objektů s polem "text")
                - sources: Seznam zdrojů (pole objektů s poli "text" a "url")
                - logical_fallacies: Seznam případných logických chyb v tvrzení (pole objektů s poli "text" a "type")
                - manipulation_techniques: Seznam případných manipulativních technik v tvrzení (pole objektů s poli "text" a "type")
                
                Odpověz pouze v JSON formátu bez dalšího textu.
            """,
            
            'detailed': """
                Jsi expertní fact-checker, který analyzuje tvrzení a určuje jejich pravdivost.
                Proveď velmi detailní analýzu následujícího tvrzení a vrať výsledek v JSON formátu s těmito poli:
                - verdict: Verdikt o pravdivosti (pravdivé, částečně pravdivé, nepravdivé, zavádějící, nelze ověřit)
                - confidence: Míra jistoty verdiktu v procentech (0-100)
                - explanation: Podrobné vysvětlení verdiktu (minimálně 5 vět)
                - context: Širší kontext tvrzení a jeho implikace
                - evidences: Seznam důkazů podporujících verdikt (pole objektů s polem "text")
                - counter_evidences: Seznam důkazů proti verdiktu, pokud existují (pole objektů s polem "text")
                - sources: Seznam zdrojů (pole objektů s poli "text" a "url")
                - logical_fallacies: Seznam případných logických chyb v tvrzení (pole objektů s poli "text", "type" a "explanation")
                - manipulation_techniques: Seznam případných manipulativních technik v tvrzení (pole objektů s poli "text", "type" a "explanation")
                - alternative_interpretations: Seznam možných alternativních interpretací tvrzení (pole objektů s polem "text")
                
                Odpověz pouze v JSON formátu bez dalšího textu.
            """
        }
        
        # Vrátí prompt pro daný typ analýzy nebo standardní prompt, pokud typ neexistuje
        return prompts.get(analysis_type, prompts['standard'])
    
    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Vytvoří chybovou odpověď v případě selhání analýzy.
        
        Args:
            error_message: Chybová zpráva
            
        Returns:
            Chybová odpověď jako slovník
        """
        return {
            "verdict": "nelze ověřit",
            "confidence": 0,
            "explanation": f"Nepodařilo se provést analýzu: {error_message}",
            "evidences": [],
            "sources": [],
            "logical_fallacies": [],
            "manipulation_techniques": []
        }
