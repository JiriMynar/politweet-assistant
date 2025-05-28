"""
Služba pro integraci s OpenAI API.

Tento modul poskytuje funkce pro komunikaci s OpenAI API
a zpracování odpovědí pro fact-checking.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List, Union

class OpenAIService:
    """
    Služba pro komunikaci s OpenAI API.
    
    Tato třída poskytuje metody pro analýzu tvrzení a generování vysvětlení
    pomocí OpenAI API.
    """
    
    BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-4"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializace služby pro OpenAI API.
        
        Args:
            api_key: OpenAI API klíč. Pokud není zadán, pokusí se ho načíst
                    z proměnné prostředí OPENAI_API_KEY.
        
        Raises:
            ValueError: Pokud API klíč není zadán ani v proměnné prostředí.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API klíč musí být zadán buď jako parametr nebo "
                "v proměnné prostředí OPENAI_API_KEY."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def analyze_claim(
        self, 
        claim_text: str, 
        analysis_type: str = "standard",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzuje tvrzení pomocí OpenAI API.
        
        Args:
            claim_text: Text tvrzení k analýze.
            analysis_type: Typ analýzy ("standard", "detailed", "quick").
            model: Model OpenAI k použití. Pokud není zadán, použije se výchozí.
        
        Returns:
            Slovník s výsledky analýzy.
        
        Raises:
            Exception: Při chybě komunikace s API.
        """
        prompt = self._get_analysis_prompt(claim_text, analysis_type)
        response = self._call_api(prompt, model)
        
        try:
            return self._parse_analysis_response(response)
        except Exception as e:
            raise Exception(f"Chyba při zpracování odpovědi API: {str(e)}")
    
    def generate_explanation(
        self, 
        claim: str, 
        analysis_result: Dict[str, Any],
        audience: str = "general",
        model: Optional[str] = None
    ) -> str:
        """
        Generuje vysvětlení výsledku analýzy.
        
        Args:
            claim: Původní tvrzení.
            analysis_result: Výsledek analýzy.
            audience: Cílové publikum ("general", "expert", "educational").
            model: Model OpenAI k použití. Pokud není zadán, použije se výchozí.
        
        Returns:
            Textové vysvětlení výsledku.
        """
        prompt = self._get_explanation_prompt(claim, analysis_result, audience)
        response = self._call_api(prompt, model)
        
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_api(
        self, 
        prompt: Union[str, List[Dict[str, str]]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Volá OpenAI API s daným promptem.
        
        Args:
            prompt: Prompt pro API (text nebo seznam zpráv).
            model: Model k použití. Pokud není zadán, použije se výchozí.
        
        Returns:
            Odpověď API jako slovník.
        
        Raises:
            Exception: Při chybě komunikace s API.
        """
        model = model or self.DEFAULT_MODEL
        
        # Příprava dat pro API
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,  # Nižší teplota pro konzistentnější odpovědi
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Chyba při komunikaci s OpenAI API: {str(e)}")
    
    def _get_analysis_prompt(self, claim_text: str, analysis_type: str) -> List[Dict[str, str]]:
        """
        Vytvoří prompt pro analýzu tvrzení.
        
        Args:
            claim_text: Text tvrzení k analýze.
            analysis_type: Typ analýzy.
        
        Returns:
            Seznam zpráv pro API.
        """
        system_prompt = """
        Jsi expertní fact-checker, který analyzuje tvrzení a určuje jejich pravdivost.
        Tvým úkolem je:
        1. Analyzovat předložené tvrzení
        2. Určit jeho pravdivost na škále (pravdivé, částečně pravdivé, nepravdivé, zavádějící, nelze ověřit)
        3. Poskytnout důkazy a zdroje podporující tvé hodnocení
        4. Identifikovat případné logické chyby nebo manipulativní techniky
        
        Odpověz ve strukturovaném formátu JSON s následujícími klíči:
        - verdict: Verdikt o pravdivosti
        - confidence: Míra jistoty (0-100)
        - explanation: Stručné vysvětlení verdiktu
        - evidence: Seznam důkazů podporujících verdikt
        - sources: Seznam zdrojů
        - logical_fallacies: Seznam případných logických chyb
        - manipulation_techniques: Seznam případných manipulativních technik
        """
        
        # Úprava promptu podle typu analýzy
        if analysis_type == "detailed":
            system_prompt += """
            Proveď detailní analýzu s důkladným rozborem všech aspektů tvrzení.
            Zahrň historický kontext, související fakta a alternativní interpretace.
            """
        elif analysis_type == "quick":
            system_prompt += """
            Proveď rychlou analýzu zaměřenou na klíčové aspekty tvrzení.
            Zaměř se na nejdůležitější fakta a zdroje.
            """
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyzuj následující tvrzení: \"{claim_text}\""}
        ]
    
    def _get_explanation_prompt(
        self, 
        claim: str, 
        analysis_result: Dict[str, Any],
        audience: str
    ) -> List[Dict[str, str]]:
        """
        Vytvoří prompt pro generování vysvětlení.
        
        Args:
            claim: Původní tvrzení.
            analysis_result: Výsledek analýzy.
            audience: Cílové publikum.
        
        Returns:
            Seznam zpráv pro API.
        """
        system_prompt = """
        Jsi expertní komunikátor, který vysvětluje výsledky fact-checkingu.
        Tvým úkolem je vytvořit srozumitelné a informativní vysvětlení výsledku analýzy.
        """
        
        # Úprava promptu podle cílového publika
        if audience == "expert":
            system_prompt += """
            Vysvětlení je určeno pro odborné publikum. Používej přesnou terminologii,
            detailní argumentaci a odborné zdroje. Předpokládej znalost tématu a metodologie.
            """
        elif audience == "educational":
            system_prompt += """
            Vysvětlení je určeno pro vzdělávací účely. Vysvětluj pojmy, uváděj příklady
            a poskytuj kontext. Zaměř se na rozvoj kritického myšlení a mediální gramotnosti.
            """
        else:  # general
            system_prompt += """
            Vysvětlení je určeno pro širokou veřejnost. Používej srozumitelný jazyk,
            jasnou strukturu a relevantní příklady. Vyhýbej se žargonu a složitým konceptům.
            """
        
        analysis_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            Tvrzení: "{claim}"
            
            Výsledek analýzy:
            {analysis_json}
            
            Vytvoř srozumitelné vysvětlení výsledku analýzy.
            """}
        ]
    
    def _parse_analysis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Zpracuje odpověď API na analýzu tvrzení.
        
        Args:
            response: Odpověď API.
        
        Returns:
            Zpracovaný výsledek analýzy.
        
        Raises:
            ValueError: Pokud odpověď neobsahuje validní JSON.
        """
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extrakce JSON z odpovědi
        try:
            # Pokus o nalezení JSON v odpovědi
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Pokud není nalezen JSON, vytvoříme strukturu manuálně
                lines = content.split("\n")
                result = {
                    "verdict": "nelze určit",
                    "confidence": 0,
                    "explanation": content,
                    "evidence": [],
                    "sources": [],
                    "logical_fallacies": [],
                    "manipulation_techniques": []
                }
                
                # Pokus o extrakci klíčových informací z textu
                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key == "verdict" or key == "verdikt":
                            result["verdict"] = value
                        elif key == "confidence" or key == "jistota":
                            try:
                                result["confidence"] = int(value.rstrip("%"))
                            except ValueError:
                                pass
                
                return result
                
        except json.JSONDecodeError:
            raise ValueError("Odpověď API neobsahuje validní JSON.")
