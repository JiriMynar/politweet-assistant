"""
Image Analyzer Module
-------------------
Modul pro analýzu obrazového obsahu, extrakci textu z obrázků a přípravu pro fact-checking.
"""

import os
import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract
from io import BytesIO
import matplotlib.pyplot as plt
import requests
from urllib.parse import urlparse

# Konfigurace logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """
    Třída pro analýzu obrazového obsahu, extrakci textu a identifikaci klíčových prvků.
    """
    
    def __init__(self):
        """Inicializace analyzátoru obrazového obsahu."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("ImageAnalyzer inicializován")
        
        # Kontrola, zda je nainstalován Tesseract OCR
        try:
            pytesseract.get_tesseract_version()
            self.ocr_available = True
        except Exception as e:
            self.logger.warning(f"Tesseract OCR není dostupný: {str(e)}")
            self.ocr_available = False
    
    def analyze(self, image_path, expertise_level='medium', analysis_length='standard'):
        """
        Analyzuje obrazový obsah, extrahuje text a identifikuje klíčové prvky.
        
        Args:
            image_path (str): Cesta k obrázku nebo URL
            expertise_level (str): Úroveň odbornosti analýzy ('basic', 'medium', 'advanced', 'expert')
            analysis_length (str): Požadovaná délka analýzy ('brief', 'standard', 'detailed', 'exhaustive')
            
        Returns:
            dict: Výsledky analýzy včetně extrahovaného textu a identifikovaných prvků
        """
        self.logger.info(f"Začínám analýzu obrázku: {image_path}")
        
        try:
            # Načtení obrázku
            image = self._load_image(image_path)
            if image is None:
                return {
                    'error': 'Nepodařilo se načíst obrázek',
                    'extracted_text': '',
                    'visual_elements': [],
                    'summary': 'Obrázek nelze analyzovat.'
                }
            
            # Extrakce textu z obrázku pomocí OCR
            extracted_text = self._extract_text(image)
            self.logger.info(f"Extrahovaný text: {len(extracted_text)} znaků")
            
            # Identifikace vizuálních prvků
            visual_elements = self._identify_visual_elements(image)
            self.logger.info(f"Identifikováno {len(visual_elements)} vizuálních prvků")
            
            # Analýza grafů a tabulek (pokud jsou přítomny)
            charts_data = self._analyze_charts_and_tables(image)
            
            # Vytvoření souhrnu
            summary = self._create_summary(extracted_text, visual_elements, charts_data)
            
            # Příprava výstupu
            result = {
                'extracted_text': extracted_text,
                'visual_elements': visual_elements,
                'charts_data': charts_data,
                'summary': summary,
                'image_metadata': self._get_image_metadata(image)
            }
            
            self.logger.info("Analýza obrázku dokončena")
            return result
            
        except Exception as e:
            self.logger.error(f"Chyba při analýze obrázku: {str(e)}", exc_info=True)
            return {
                'error': f'Chyba při analýze obrázku: {str(e)}',
                'extracted_text': '',
                'visual_elements': [],
                'summary': 'Došlo k chybě při analýze obrázku.'
            }
    
    def _load_image(self, image_path):
        """
        Načte obrázek z lokální cesty nebo URL.
        
        Args:
            image_path (str): Cesta k obrázku nebo URL
            
        Returns:
            PIL.Image: Načtený obrázek nebo None v případě chyby
        """
        try:
            # Kontrola, zda se jedná o URL
            if image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path, stream=True)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                # Lokální soubor
                image = Image.open(image_path)
            
            return image
        except Exception as e:
            self.logger.error(f"Chyba při načítání obrázku: {str(e)}", exc_info=True)
            return None
    
    def _extract_text(self, image):
        """
        Extrahuje text z obrázku pomocí OCR.
        
        Args:
            image (PIL.Image): Obrázek k analýze
            
        Returns:
            str: Extrahovaný text
        """
        if not self.ocr_available:
            self.logger.warning("OCR není dostupné, text nelze extrahovat")
            return "OCR není dostupné, text nelze extrahovat."
        
        try:
            # Převod na numpy array pro OpenCV
            img_np = np.array(image)
            
            # Převod na šedotónový obrázek
            if len(img_np.shape) == 3 and img_np.shape[2] == 3:
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_np
            
            # Aplikace adaptivního prahování pro zlepšení čitelnosti textu
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Extrakce textu pomocí Tesseract OCR
            text = pytesseract.image_to_string(thresh, lang='ces+eng')
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"Chyba při extrakci textu: {str(e)}", exc_info=True)
            return "Chyba při extrakci textu."
    
    def _identify_visual_elements(self, image):
        """
        Identifikuje vizuální prvky v obrázku (grafy, tabulky, diagramy, atd.).
        
        Args:
            image (PIL.Image): Obrázek k analýze
            
        Returns:
            list: Seznam identifikovaných vizuálních prvků
        """
        visual_elements = []
        
        try:
            # Převod na numpy array pro OpenCV
            img_np = np.array(image)
            
            # Převod na šedotónový obrázek
            if len(img_np.shape) == 3 and img_np.shape[2] == 3:
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_np
            
            # Detekce hran
            edges = cv2.Canny(gray, 50, 150)
            
            # Hledání kontur
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrování kontur podle velikosti
            min_contour_area = 0.01 * image.width * image.height
            significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
            
            # Identifikace obdélníkových oblastí (potenciální tabulky nebo grafy)
            for i, contour in enumerate(significant_contours):
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                element_type = "unknown"
                confidence = 0.0
                
                # Klasifikace typu vizuálního prvku
                if 0.8 <= aspect_ratio <= 1.2:
                    # Přibližně čtvercový tvar - pravděpodobně graf
                    element_type = "graph"
                    confidence = 0.7
                elif aspect_ratio > 1.5:
                    # Široký obdélník - pravděpodobně tabulka
                    element_type = "table"
                    confidence = 0.6
                elif aspect_ratio < 0.7:
                    # Vysoký obdélník - pravděpodobně diagram
                    element_type = "diagram"
                    confidence = 0.5
                
                visual_elements.append({
                    'id': i,
                    'type': element_type,
                    'confidence': confidence,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h},
                    'aspect_ratio': aspect_ratio
                })
            
        except Exception as e:
            self.logger.error(f"Chyba při identifikaci vizuálních prvků: {str(e)}", exc_info=True)
        
        return visual_elements
    
    def _analyze_charts_and_tables(self, image):
        """
        Analyzuje grafy a tabulky v obrázku.
        
        Args:
            image (PIL.Image): Obrázek k analýze
            
        Returns:
            dict: Výsledky analýzy grafů a tabulek
        """
        # Toto je zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro rozpoznávání a analýzu grafů a tabulek
        
        charts_data = {
            'detected': False,
            'chart_types': [],
            'data_points': [],
            'tables': []
        }
        
        try:
            # Převod na numpy array pro OpenCV
            img_np = np.array(image)
            
            # Převod na šedotónový obrázek
            if len(img_np.shape) == 3 and img_np.shape[2] == 3:
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_np
            
            # Detekce hran
            edges = cv2.Canny(gray, 50, 150)
            
            # Hledání přímek pomocí Houghovy transformace
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is not None and len(lines) > 10:
                # Velký počet přímek může indikovat přítomnost tabulky
                charts_data['detected'] = True
                charts_data['chart_types'].append('table')
            
            # Detekce kruhů (potenciální koláčové grafy)
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                param1=50, param2=30, minRadius=30, maxRadius=100
            )
            
            if circles is not None:
                charts_data['detected'] = True
                charts_data['chart_types'].append('pie_chart')
            
        except Exception as e:
            self.logger.error(f"Chyba při analýze grafů a tabulek: {str(e)}", exc_info=True)
        
        return charts_data
    
    def _get_image_metadata(self, image):
        """
        Získá metadata obrázku.
        
        Args:
            image (PIL.Image): Obrázek k analýze
            
        Returns:
            dict: Metadata obrázku
        """
        metadata = {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode
        }
        
        # Pokus o získání EXIF dat (pokud jsou k dispozici)
        try:
            exif_data = image._getexif()
            if exif_data:
                metadata['exif'] = {}
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    metadata['exif'][tag_name] = value
        except (AttributeError, KeyError, IndexError):
            pass
        
        return metadata
    
    def _create_summary(self, extracted_text, visual_elements, charts_data):
        """
        Vytvoří souhrn analyzovaného obrázku.
        
        Args:
            extracted_text (str): Extrahovaný text z obrázku
            visual_elements (list): Seznam identifikovaných vizuálních prvků
            charts_data (dict): Výsledky analýzy grafů a tabulek
            
        Returns:
            str: Souhrn obrázku
        """
        summary_parts = []
        
        # Informace o extrahovaném textu
        if extracted_text:
            text_length = len(extracted_text)
            if text_length > 500:
                summary_parts.append(f"Obrázek obsahuje velké množství textu ({text_length} znaků).")
            elif text_length > 100:
                summary_parts.append(f"Obrázek obsahuje střední množství textu ({text_length} znaků).")
            elif text_length > 0:
                summary_parts.append(f"Obrázek obsahuje malé množství textu ({text_length} znaků).")
        else:
            summary_parts.append("Obrázek neobsahuje žádný čitelný text.")
        
        # Informace o vizuálních prvcích
        if visual_elements:
            element_types = {}
            for element in visual_elements:
                element_type = element['type']
                element_types[element_type] = element_types.get(element_type, 0) + 1
            
            for element_type, count in element_types.items():
                if element_type == "graph":
                    summary_parts.append(f"Obrázek obsahuje {count} grafů.")
                elif element_type == "table":
                    summary_parts.append(f"Obrázek obsahuje {count} tabulek.")
                elif element_type == "diagram":
                    summary_parts.append(f"Obrázek obsahuje {count} diagramů.")
                else:
                    summary_parts.append(f"Obrázek obsahuje {count} neidentifikovaných vizuálních prvků.")
        
        # Informace o grafech a tabulkách
        if charts_data['detected']:
            chart_types = charts_data['chart_types']
            if 'pie_chart' in chart_types:
                summary_parts.append("Obrázek obsahuje koláčový graf.")
            if 'table' in chart_types:
                summary_parts.append("Obrázek obsahuje tabulku s daty.")
        
        # Sestavení souhrnu
        if summary_parts:
            return " ".join(summary_parts)
        else:
            return "Obrázek neobsahuje žádné významné prvky k analýze."
