"""
Služba pro integraci s OpenAI API.

Tento modul poskytuje služby pro komunikaci s OpenAI API a analýzu tvrzení.
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional, List, Union

class OpenAIService:
    """
    Služba pro komunikaci s OpenAI API.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", api_version: str = None):
        """
        Inicializace služby.
        
        Args:
            api_key: OpenAI API klíč
            model: Model OpenAI API k použití
            api_version: Verze OpenAI API
        """
        if not self._validate_api_key(api_key):
            raise ValueError("Neplatný formát API klíče. Klíč by měl začínat 'sk-'.")
            
        self.api_key = api_key
        self.model = model
        self.api_version = api_version
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        # Sestavení hlaviček požadavku
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Přidání verze API, pokud je specifikována
        if api_version:
            self.headers["OpenAI-Version"] = api_version
    
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
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1000
        }
        
        # Přidání formátu odpovědi, pokud je podporován
        if self._supports_response_format():
            data["response_format"] = {"type": "json_object"}
        
        try:
            # Odeslání požadavku na API s mechanismem opakování
            result = self._send_request_with_retry(data)
            
            # Zpracování odpovědi
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parsování JSON odpovědi
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError:
                # Pokud odpověď není validní JSON, vrátíme ji jako text
                analysis_result = {
                    "verdict": "nelze ověřit",
                    "confidence": 0,
                    "explanation": "Nepodařilo se zpracovat odpověď API jako JSON. Původní odpověď: " + content[:200] + "..."
                }
            
            # Přidání typu analýzy do výsledku
            analysis_result["analysis_type"] = analysis_type
            
            return analysis_result
        
        except requests.exceptions.RequestException as e:
            # Ošetření chyb při komunikaci s API
            print(f"Chyba při komunikaci s OpenAI API: {str(e)}")
            return self._get_error_response(f"Chyba komunikace: {str(e)}")
        
        except json.JSONDecodeError as e:
            # Ošetření chyb při parsování JSON
            print(f"Chyba při parsování odpovědi: {str(e)}")
            return self._get_error_response("Neplatná odpověď od API")
        
        except ValueError as e:
            # Ošetření chyb validace
            print(f"Chyba validace: {str(e)}")
            return self._get_error_response(str(e))
        
        except Exception as e:
            # Ošetření ostatních chyb
            print(f"Neočekávaná chyba: {str(e)}")
            return self._get_error_response(f"Neočekávaná chyba: {str(e)}")
    
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
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validuje formát API klíče.
        
        Args:
            api_key: OpenAI API klíč k validaci
            
        Returns:
            True pokud je klíč validní, jinak False
        """
        # Základní validace - klíč by měl začínat "sk-" a mít určitou délku
        return api_key and isinstance(api_key, str) and api_key.startswith("sk-") and len(api_key) > 20
    
    def _supports_response_format(self) -> bool:
        """
        Zjistí, zda aktuální model podporuje parametr response_format.
        
        Returns:
            True pokud model podporuje response_format, jinak False
        """
        # Seznam modelů, které podporují response_format
        supported_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]
        
        # Kontrola, zda aktuální model podporuje response_format
        for model in supported_models:
            if model in self.model:
                return True
        
        return False
    
    def _send_request_with_retry(self, data: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Odešle požadavek na API s mechanismem opakování.
        
        Args:
            data: Data požadavku
            max_retries: Maximální počet pokusů
            
        Returns:
            Odpověď API jako slovník
            
        Raises:
            ValueError: Pokud je API klíč neplatný nebo model není dostupný
            requests.exceptions.RequestException: Pokud dojde k chybě při komunikaci s API
        """
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
                
                # Zpracování různých HTTP stavových kódů
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise ValueError("Neplatný API klíč nebo nedostatečná oprávnění")
                elif response.status_code == 429:
                    # Rate limiting - počkáme a zkusíme znovu
                    retry_count += 1
                    wait_time = 2 ** retry_count  # Exponenciální odstup
                    print(f"Rate limit překročen, čekám {wait_time} sekund...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 404:
                    raise ValueError(f"Model není dostupný: {data.get('model')}")
                else:
                    # Pokus o získání chybové zprávy z odpovědi
                    error_msg = "Neznámá chyba"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Neznámá chyba")
                    except:
                        error_msg = f"HTTP chyba {response.status_code}"
                    
                    raise requests.exceptions.RequestException(f"API chyba: {error_msg}")
                    
            except (requests.exceptions.RequestException, ValueError) as e:
                last_error = e
                retry_count += 1
                
                # Pokud se jedná o neplatný API klíč nebo nedostupný model, nemá smysl opakovat
                if isinstance(e, ValueError) and ("API klíč" in str(e) or "model není dostupný" in str(e)):
                    raise e
                
                if retry_count >= max_retries:
                    break
                
                wait_time = 2 ** retry_count  # Exponenciální odstup
                print(f"Chyba při požadavku, čekám {wait_time} sekund před opakováním...")
                time.sleep(wait_time)
        
        # Pokud jsme vyčerpali všechny pokusy, vyvoláme poslední chybu
        if last_error:
            raise last_error
        
        raise RuntimeError("Překročen maximální počet pokusů")
    
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
