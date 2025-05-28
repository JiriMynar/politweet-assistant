"""
Video Analyzer Module
-------------------
Modul pro analýzu video obsahu, extrakci klíčových snímků, transkripci řeči a přípravu pro fact-checking.
"""

import os
import logging
import cv2
import numpy as np
import tempfile
import requests
from io import BytesIO
import subprocess
import json
from PIL import Image
import speech_recognition as sr
from pydub import AudioSegment

# Import vlastních modulů
from services.image_analyzer import ImageAnalyzer
from services.audio_analyzer import AudioAnalyzer

# Konfigurace logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAnalyzer:
    """
    Třída pro analýzu video obsahu, extrakci klíčových snímků, transkripci řeči a identifikaci klíčových prvků.
    """
    
    def __init__(self):
        """Inicializace analyzátoru video obsahu."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("VideoAnalyzer inicializován")
        
        # Inicializace analyzátorů pro obrázky a audio
        self.image_analyzer = ImageAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
    
    def analyze(self, video_path, language='cs', expertise_level='medium', analysis_length='standard'):
        """
        Analyzuje video obsah, extrahuje klíčové snímky, provádí transkripci řeči a identifikuje klíčové prvky.
        
        Args:
            video_path (str): Cesta k video souboru nebo URL
            language (str): Kód jazyka pro rozpoznávání řeči ('cs', 'en', 'sk', atd.)
            expertise_level (str): Úroveň odbornosti analýzy ('basic', 'medium', 'advanced', 'expert')
            analysis_length (str): Požadovaná délka analýzy ('brief', 'standard', 'detailed', 'exhaustive')
            
        Returns:
            dict: Výsledky analýzy včetně transkripce, klíčových snímků a identifikovaných prvků
        """
        self.logger.info(f"Začínám analýzu video souboru: {video_path}")
        
        try:
            # Načtení video souboru
            video_data = self._load_video(video_path)
            if video_data is None:
                return {
                    'error': 'Nepodařilo se načíst video soubor',
                    'transcription': '',
                    'key_frames': [],
                    'summary': 'Video nelze analyzovat.'
                }
            
            # Extrakce klíčových snímků
            key_frames = self._extract_key_frames(video_data, analysis_length)
            self.logger.info(f"Extrahováno {len(key_frames)} klíčových snímků")
            
            # Analýza klíčových snímků
            frame_analyses = self._analyze_key_frames(key_frames, expertise_level, analysis_length)
            self.logger.info(f"Analyzovány klíčové snímky")
            
            # Extrakce a analýza audio stopy
            audio_analysis = self._analyze_audio_track(video_data, language, expertise_level, analysis_length)
            self.logger.info(f"Analyzována audio stopa")
            
            # Detekce scén a přechodů
            scenes = self._detect_scenes(video_data)
            self.logger.info(f"Detekováno {len(scenes)} scén")
            
            # Detekce textu ve videu (titulky, popisky)
            text_detections = self._detect_text_in_video(key_frames)
            self.logger.info(f"Detekován text ve videu")
            
            # Vytvoření souhrnu
            summary = self._create_summary(video_data, key_frames, audio_analysis, scenes, text_detections)
            
            # Příprava výstupu
            result = {
                'video_metadata': self._get_video_metadata(video_data),
                'key_frames': [
                    {
                        'timestamp': frame['timestamp'],
                        'analysis': frame_analyses[i]
                    } for i, frame in enumerate(key_frames)
                ],
                'audio_analysis': audio_analysis,
                'scenes': scenes,
                'text_detections': text_detections,
                'summary': summary
            }
            
            self.logger.info("Analýza video souboru dokončena")
            return result
            
        except Exception as e:
            self.logger.error(f"Chyba při analýze video souboru: {str(e)}", exc_info=True)
            return {
                'error': f'Chyba při analýze video souboru: {str(e)}',
                'transcription': '',
                'key_frames': [],
                'summary': 'Došlo k chybě při analýze video souboru.'
            }
    
    def _load_video(self, video_path):
        """
        Načte video soubor z lokální cesty nebo URL.
        
        Args:
            video_path (str): Cesta k video souboru nebo URL
            
        Returns:
            dict: Načtená video data nebo None v případě chyby
        """
        try:
            # Kontrola, zda se jedná o URL
            if video_path.startswith(('http://', 'https://')):
                # Stažení do dočasného souboru
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    response = requests.get(video_path, stream=True)
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                # Načtení videa
                cap = cv2.VideoCapture(temp_path)
                local_path = temp_path
            else:
                # Lokální soubor
                cap = cv2.VideoCapture(video_path)
                local_path = video_path
            
            # Kontrola, zda se video podařilo otevřít
            if not cap.isOpened():
                self.logger.error(f"Nepodařilo se otevřít video: {video_path}")
                return None
            
            # Získání základních vlastností videa
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Vytvoření slovníku s video daty
            video_data = {
                'cap': cap,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'path': video_path,
                'local_path': local_path
            }
            
            return video_data
        except Exception as e:
            self.logger.error(f"Chyba při načítání video souboru: {str(e)}", exc_info=True)
            return None
    
    def _extract_key_frames(self, video_data, analysis_length):
        """
        Extrahuje klíčové snímky z videa.
        
        Args:
            video_data (dict): Načtená video data
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            list: Seznam klíčových snímků
        """
        try:
            cap = video_data['cap']
            frame_count = video_data['frame_count']
            fps = video_data['fps']
            duration = video_data['duration']
            
            # Určení počtu klíčových snímků podle požadované délky analýzy
            num_key_frames = self._get_key_frames_count(analysis_length)
            
            # Omezení počtu snímků pro velmi krátká videa
            if frame_count < num_key_frames * 2:
                num_key_frames = max(1, frame_count // 2)
            
            # Výpočet intervalu mezi klíčovými snímky
            if num_key_frames > 1:
                interval = frame_count / (num_key_frames - 1)
            else:
                interval = frame_count
            
            key_frames = []
            
            # Extrakce klíčových snímků v pravidelných intervalech
            for i in range(num_key_frames):
                frame_idx = int(i * interval)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Převod z BGR na RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Výpočet časové značky
                    timestamp = frame_idx / fps if fps > 0 else 0
                    
                    # Uložení snímku do seznamu
                    key_frames.append({
                        'frame': frame_rgb,
                        'timestamp': timestamp,
                        'frame_idx': frame_idx
                    })
            
            # Reset video capture pro další použití
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            return key_frames
        except Exception as e:
            self.logger.error(f"Chyba při extrakci klíčových snímků: {str(e)}", exc_info=True)
            return []
    
    def _get_key_frames_count(self, analysis_length):
        """
        Určí počet klíčových snímků podle požadované délky analýzy.
        
        Args:
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            int: Počet klíčových snímků
        """
        counts = {
            'brief': 3,
            'standard': 5,
            'detailed': 8,
            'exhaustive': 12
        }
        
        return counts.get(analysis_length, 5)
    
    def _analyze_key_frames(self, key_frames, expertise_level, analysis_length):
        """
        Analyzuje klíčové snímky pomocí ImageAnalyzer.
        
        Args:
            key_frames (list): Seznam klíčových snímků
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            list: Seznam analýz klíčových snímků
        """
        frame_analyses = []
        
        for i, frame_data in enumerate(key_frames):
            try:
                # Uložení snímku do dočasného souboru
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_path = temp_file.name
                    frame_pil = Image.fromarray(frame_data['frame'])
                    frame_pil.save(temp_path)
                
                # Analýza snímku
                analysis = self.image_analyzer.analyze(temp_path, expertise_level, analysis_length)
                
                # Odstranění dočasného souboru
                os.unlink(temp_path)
                
                frame_analyses.append(analysis)
            except Exception as e:
                self.logger.error(f"Chyba při analýze snímku {i}: {str(e)}", exc_info=True)
                frame_analyses.append({
                    'error': f'Chyba při analýze snímku: {str(e)}',
                    'extracted_text': '',
                    'visual_elements': []
                })
        
        return frame_analyses
    
    def _analyze_audio_track(self, video_data, language, expertise_level, analysis_length):
        """
        Extrahuje a analyzuje audio stopu z videa.
        
        Args:
            video_data (dict): Načtená video data
            language (str): Kód jazyka pro rozpoznávání řeči
            expertise_level (str): Úroveň odbornosti analýzy
            analysis_length (str): Požadovaná délka analýzy
            
        Returns:
            dict: Výsledky analýzy audio stopy
        """
        try:
            # Extrakce audio stopy do dočasného souboru
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_audio_path = temp_file.name
            
            # Použití ffmpeg pro extrakci audio stopy
            video_path = video_data['local_path']
            cmd = [
                'ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', temp_audio_path, '-y'
            ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Chyba při extrakci audio stopy: {e.stderr.decode()}")
                return {
                    'error': 'Nepodařilo se extrahovat audio stopu',
                    'transcription': '',
                    'audio_features': {}
                }
            
            # Analýza audio stopy
            audio_analysis = self.audio_analyzer.analyze(temp_audio_path, language, expertise_level, analysis_length)
            
            # Odstranění dočasného souboru
            os.unlink(temp_audio_path)
            
            return audio_analysis
        except Exception as e:
            self.logger.error(f"Chyba při analýze audio stopy: {str(e)}", exc_info=True)
            return {
                'error': f'Chyba při analýze audio stopy: {str(e)}',
                'transcription': '',
                'audio_features': {}
            }
    
    def _detect_scenes(self, video_data):
        """
        Detekuje scény a přechody ve videu.
        
        Args:
            video_data (dict): Načtená video data
            
        Returns:
            list: Seznam detekovaných scén
        """
        try:
            cap = video_data['cap']
            fps = video_data['fps']
            frame_count = video_data['frame_count']
            
            # Reset video capture
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            scenes = []
            prev_frame = None
            current_scene = {'start': 0, 'end': 0, 'changes': []}
            
            # Parametry pro detekci změn scén
            threshold = 30.0  # Práh pro detekci změny scény
            min_scene_length = int(fps * 1.5)  # Minimální délka scény (1.5 sekundy)
            
            for frame_idx in range(0, frame_count, max(1, int(fps / 2))):  # Kontrola každých 0.5 sekundy
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Převod na šedotónový obrázek a zmenšení pro rychlejší zpracování
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (160, 90))
                
                if prev_frame is not None:
                    # Výpočet rozdílu mezi snímky
                    diff = cv2.absdiff(gray, prev_frame)
                    diff_mean = np.mean(diff)
                    
                    # Detekce změny scény
                    if diff_mean > threshold and (frame_idx - current_scene['start']) > min_scene_length:
                        # Ukončení aktuální scény
                        current_scene['end'] = frame_idx
                        current_scene['duration'] = (current_scene['end'] - current_scene['start']) / fps
                        scenes.append(current_scene)
                        
                        # Začátek nové scény
                        current_scene = {'start': frame_idx, 'end': frame_idx, 'changes': []}
                    
                    # Zaznamenání významné změny
                    if diff_mean > threshold / 2:
                        current_scene['changes'].append({
                            'frame': frame_idx,
                            'timestamp': frame_idx / fps,
                            'magnitude': diff_mean
                        })
                
                prev_frame = gray
            
            # Přidání poslední scény
            if current_scene['start'] < frame_count - 1:
                current_scene['end'] = frame_count - 1
                current_scene['duration'] = (current_scene['end'] - current_scene['start']) / fps
                scenes.append(current_scene)
            
            # Reset video capture pro další použití
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Převod časových značek na sekundy
            for scene in scenes:
                scene['start_time'] = scene['start'] / fps
                scene['end_time'] = scene['end'] / fps
            
            return scenes
        except Exception as e:
            self.logger.error(f"Chyba při detekci scén: {str(e)}", exc_info=True)
            return []
    
    def _detect_text_in_video(self, key_frames):
        """
        Detekuje text ve videu (titulky, popisky).
        
        Args:
            key_frames (list): Seznam klíčových snímků
            
        Returns:
            list: Seznam detekovaného textu
        """
        text_detections = []
        
        for frame_data in key_frames:
            try:
                # Uložení snímku do dočasného souboru
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_path = temp_file.name
                    frame_pil = Image.fromarray(frame_data['frame'])
                    frame_pil.save(temp_path)
                
                # Extrakce textu pomocí OCR
                extracted_text = self.image_analyzer._extract_text(frame_pil)
                
                # Odstranění dočasného souboru
                os.unlink(temp_path)
                
                # Přidání detekce, pokud byl nalezen text
                if extracted_text and len(extracted_text) > 5:
                    text_detections.append({
                        'timestamp': frame_data['timestamp'],
                        'frame_idx': frame_data['frame_idx'],
                        'text': extracted_text
                    })
            except Exception as e:
                self.logger.error(f"Chyba při detekci textu ve snímku: {str(e)}", exc_info=True)
        
        return text_detections
    
    def _get_video_metadata(self, video_data):
        """
        Získá metadata video souboru.
        
        Args:
            video_data (dict): Načtená video data
            
        Returns:
            dict: Metadata video souboru
        """
        metadata = {
            'duration': video_data['duration'],
            'fps': video_data['fps'],
            'frame_count': video_data['frame_count'],
            'width': video_data['width'],
            'height': video_data['height'],
            'aspect_ratio': video_data['width'] / video_data['height'] if video_data['height'] > 0 else 0
        }
        
        # Pokus o získání dalších metadat pomocí ffprobe
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_data['local_path']
            ]
            
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ffprobe_data = json.loads(result.stdout)
            
            # Extrakce užitečných informací
            if 'format' in ffprobe_data:
                format_data = ffprobe_data['format']
                metadata['format'] = format_data.get('format_name', 'unknown')
                metadata['size'] = int(format_data.get('size', 0))
                metadata['bit_rate'] = int(format_data.get('bit_rate', 0))
            
            # Informace o video a audio stopách
            if 'streams' in ffprobe_data:
                for stream in ffprobe_data['streams']:
                    if stream.get('codec_type') == 'video':
                        metadata['video_codec'] = stream.get('codec_name', 'unknown')
                    elif stream.get('codec_type') == 'audio':
                        metadata['audio_codec'] = stream.get('codec_name', 'unknown')
                        metadata['audio_channels'] = stream.get('channels', 0)
                        metadata['audio_sample_rate'] = stream.get('sample_rate', 0)
        except Exception as e:
            self.logger.warning(f"Nepodařilo se získat rozšířená metadata: {str(e)}")
        
        return metadata
    
    def _create_summary(self, video_data, key_frames, audio_analysis, scenes, text_detections):
        """
        Vytvoří souhrn analyzovaného video souboru.
        
        Args:
            video_data (dict): Načtená video data
            key_frames (list): Seznam klíčových snímků
            audio_analysis (dict): Výsledky analýzy audio stopy
            scenes (list): Seznam detekovaných scén
            text_detections (list): Seznam detekovaného textu
            
        Returns:
            str: Souhrn video souboru
        """
        summary_parts = []
        
        # Základní informace o videu
        duration_min = int(video_data['duration'] // 60)
        duration_sec = int(video_data['duration'] % 60)
        summary_parts.append(f"Video o délce {duration_min}:{duration_sec:02d} minut.")
        
        # Informace o rozlišení
        resolution_category = "nízké"
        if video_data['width'] >= 1920 or video_data['height'] >= 1080:
            resolution_category = "vysoké (HD)"
        elif video_data['width'] >= 1280 or video_data['height'] >= 720:
            resolution_category = "střední (HD)"
        summary_parts.append(f"Video má {resolution_category} rozlišení ({video_data['width']}x{video_data['height']}).")
        
        # Informace o scénách
        if scenes:
            summary_parts.append(f"Video obsahuje {len(scenes)} různých scén.")
        
        # Informace o detekovaném textu
        if text_detections:
            summary_parts.append(f"Ve videu byl detekován text v {len(text_detections)} snímcích.")
        
        # Informace z audio analýzy
        if 'transcription' in audio_analysis and audio_analysis['transcription'] and not audio_analysis['transcription'].startswith("Chyba"):
            words = audio_analysis['transcription'].split()
            word_count = len(words)
            if word_count > 0:
                summary_parts.append(f"Audio stopa obsahuje přibližně {word_count} slov.")
        
        if 'audio_features' in audio_analysis and 'content_type' in audio_analysis['audio_features']:
            content_type = audio_analysis['audio_features']['content_type']
            if content_type == "speech":
                summary_parts.append("Audio stopa obsahuje převážně řeč.")
            elif content_type == "music":
                summary_parts.append("Audio stopa obsahuje převážně hudbu.")
            elif content_type == "mixed":
                summary_parts.append("Audio stopa obsahuje kombinaci řeči a hudby.")
        
        # Sestavení souhrnu
        if summary_parts:
            return " ".join(summary_parts)
        else:
            return "Video neobsahuje žádné významné prvky k analýze."
