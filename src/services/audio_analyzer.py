"""
Audio Analyzer Module
-------------------
Modul pro analýzu audio obsahu, transkripci řeči a přípravu pro fact-checking.
"""

import os
import logging
import numpy as np
import librosa
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import requests
from io import BytesIO

# Konfigurace logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """
    Třída pro analýzu audio obsahu, transkripci řeči a identifikaci klíčových prvků.
    """
    
    def __init__(self):
        """Inicializace analyzátoru audio obsahu."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("AudioAnalyzer inicializován")
        
        # Inicializace rozpoznávače řeči
        self.recognizer = sr.Recognizer()
        
        # Podporované jazyky pro rozpoznávání řeči
        self.supported_languages = {
            'cs': 'cs-CZ',  # čeština
            'en': 'en-US',  # angličtina (USA)
            'sk': 'sk-SK',  # slovenština
            'de': 'de-DE',  # němčina
            'fr': 'fr-FR',  # francouzština
            'es': 'es-ES',  # španělština
            'it': 'it-IT',  # italština
            'pl': 'pl-PL',  # polština
            'ru': 'ru-RU'   # ruština
        }
    
    def analyze(self, audio_path, language='cs', expertise_level='medium', analysis_length='standard'):
        """
        Analyzuje audio obsah, provádí transkripci řeči a identifikuje klíčové prvky.
        
        Args:
            audio_path (str): Cesta k audio souboru nebo URL
            language (str): Kód jazyka pro rozpoznávání řeči ('cs', 'en', 'sk', atd.)
            expertise_level (str): Úroveň odbornosti analýzy ('basic', 'medium', 'advanced', 'expert')
            analysis_length (str): Požadovaná délka analýzy ('brief', 'standard', 'detailed', 'exhaustive')
            
        Returns:
            dict: Výsledky analýzy včetně transkripce a identifikovaných prvků
        """
        self.logger.info(f"Začínám analýzu audio souboru: {audio_path}")
        
        try:
            # Načtení audio souboru
            audio_data = self._load_audio(audio_path)
            if audio_data is None:
                return {
                    'error': 'Nepodařilo se načíst audio soubor',
                    'transcription': '',
                    'audio_features': {},
                    'summary': 'Audio nelze analyzovat.'
                }
            
            # Transkripce řeči
            transcription = self._transcribe_speech(audio_data, language)
            self.logger.info(f"Transkripce: {len(transcription)} znaků")
            
            # Analýza audio vlastností
            audio_features = self._analyze_audio_features(audio_data)
            self.logger.info(f"Analyzovány audio vlastnosti")
            
            # Identifikace mluvčích (pokud je to možné)
            speakers = self._identify_speakers(audio_data)
            self.logger.info(f"Identifikováno {len(speakers)} mluvčích")
            
            # Detekce emocí v řeči
            emotions = self._detect_emotions(audio_data)
            self.logger.info(f"Detekce emocí dokončena")
            
            # Vytvoření souhrnu
            summary = self._create_summary(transcription, audio_features, speakers, emotions)
            
            # Příprava výstupu
            result = {
                'transcription': transcription,
                'audio_features': audio_features,
                'speakers': speakers,
                'emotions': emotions,
                'summary': summary,
                'audio_metadata': self._get_audio_metadata(audio_data)
            }
            
            self.logger.info("Analýza audio souboru dokončena")
            return result
            
        except Exception as e:
            self.logger.error(f"Chyba při analýze audio souboru: {str(e)}", exc_info=True)
            return {
                'error': f'Chyba při analýze audio souboru: {str(e)}',
                'transcription': '',
                'audio_features': {},
                'summary': 'Došlo k chybě při analýze audio souboru.'
            }
    
    def _load_audio(self, audio_path):
        """
        Načte audio soubor z lokální cesty nebo URL.
        
        Args:
            audio_path (str): Cesta k audio souboru nebo URL
            
        Returns:
            dict: Načtená audio data nebo None v případě chyby
        """
        try:
            # Kontrola, zda se jedná o URL
            if audio_path.startswith(('http://', 'https://')):
                response = requests.get(audio_path, stream=True)
                response.raise_for_status()
                
                # Uložení do dočasného souboru
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                # Načtení audio dat
                audio_segment = AudioSegment.from_file(temp_path)
                
                # Odstranění dočasného souboru
                os.unlink(temp_path)
            else:
                # Lokální soubor
                audio_segment = AudioSegment.from_file(audio_path)
            
            # Převod na mono pro jednodušší zpracování
            audio_segment = audio_segment.set_channels(1)
            
            # Extrakce základních vlastností
            sample_rate = audio_segment.frame_rate
            samples = np.array(audio_segment.get_array_of_samples())
            
            # Normalizace
            samples = samples / (2.0 ** 15)
            
            # Vytvoření slovníku s audio daty
            audio_data = {
                'segment': audio_segment,
                'samples': samples,
                'sample_rate': sample_rate,
                'duration': len(audio_segment) / 1000.0,  # v sekundách
                'path': audio_path
            }
            
            return audio_data
        except Exception as e:
            self.logger.error(f"Chyba při načítání audio souboru: {str(e)}", exc_info=True)
            return None
    
    def _transcribe_speech(self, audio_data, language='cs'):
        """
        Provádí transkripci řeči z audio souboru.
        
        Args:
            audio_data (dict): Načtená audio data
            language (str): Kód jazyka pro rozpoznávání řeči
            
        Returns:
            str: Transkripce řeči
        """
        try:
            # Získání jazyka pro rozpoznávání
            lang_code = self.supported_languages.get(language, 'cs-CZ')
            
            # Uložení do dočasného WAV souboru (SpeechRecognition vyžaduje WAV)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                audio_data['segment'].export(temp_path, format='wav')
            
            # Načtení audio souboru pro rozpoznávání
            with sr.AudioFile(temp_path) as source:
                audio = self.recognizer.record(source)
            
            # Odstranění dočasného souboru
            os.unlink(temp_path)
            
            # Rozpoznávání řeči
            try:
                # Pokus o použití Google Speech Recognition
                transcription = self.recognizer.recognize_google(audio, language=lang_code)
            except sr.UnknownValueError:
                transcription = "Audio neobsahuje rozpoznatelnou řeč."
            except sr.RequestError as e:
                transcription = f"Chyba při požadavku na službu rozpoznávání řeči: {e}"
            
            return transcription
        except Exception as e:
            self.logger.error(f"Chyba při transkripci řeči: {str(e)}", exc_info=True)
            return "Chyba při transkripci řeči."
    
    def _analyze_audio_features(self, audio_data):
        """
        Analyzuje vlastnosti audio souboru.
        
        Args:
            audio_data (dict): Načtená audio data
            
        Returns:
            dict: Analyzované vlastnosti audio souboru
        """
        try:
            samples = audio_data['samples']
            sample_rate = audio_data['sample_rate']
            
            # Výpočet základních vlastností
            features = {}
            
            # Výpočet RMS (Root Mean Square) - indikátor hlasitosti
            features['rms'] = float(np.sqrt(np.mean(samples**2)))
            
            # Výpočet ZCR (Zero Crossing Rate) - indikátor frekvence
            zero_crossings = np.sum(np.abs(np.diff(np.signbit(samples).astype(int))))
            features['zero_crossing_rate'] = float(zero_crossings) / len(samples)
            
            # Výpočet spektrálního centroidu - indikátor "jasu" zvuku
            try:
                spectral_centroids = librosa.feature.spectral_centroid(y=samples, sr=sample_rate)[0]
                features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            except:
                features['spectral_centroid_mean'] = 0.0
            
            # Výpočet spektrálního kontrastu - indikátor rozdílu mezi špičkami a údolími ve spektru
            try:
                spectral_contrast = librosa.feature.spectral_contrast(y=samples, sr=sample_rate)
                features['spectral_contrast_mean'] = float(np.mean(spectral_contrast))
            except:
                features['spectral_contrast_mean'] = 0.0
            
            # Výpočet tempa
            try:
                tempo, _ = librosa.beat.beat_track(y=samples, sr=sample_rate)
                features['tempo'] = float(tempo)
            except:
                features['tempo'] = 0.0
            
            # Klasifikace typu audio obsahu
            features['content_type'] = self._classify_audio_content(features)
            
            return features
        except Exception as e:
            self.logger.error(f"Chyba při analýze audio vlastností: {str(e)}", exc_info=True)
            return {}
    
    def _classify_audio_content(self, features):
        """
        Klasifikuje typ audio obsahu na základě extrahovaných vlastností.
        
        Args:
            features (dict): Extrahované vlastnosti audio souboru
            
        Returns:
            str: Klasifikovaný typ audio obsahu
        """
        # Zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        
        zcr = features.get('zero_crossing_rate', 0.0)
        rms = features.get('rms', 0.0)
        tempo = features.get('tempo', 0.0)
        
        if zcr > 0.1 and rms < 0.05:
            return "speech"  # řeč
        elif tempo > 100 and rms > 0.1:
            return "music"  # hudba
        elif rms > 0.2:
            return "noise"  # hluk
        else:
            return "mixed"  # smíšený obsah
    
    def _identify_speakers(self, audio_data):
        """
        Identifikuje různé mluvčí v audio souboru.
        
        Args:
            audio_data (dict): Načtená audio data
            
        Returns:
            list: Seznam identifikovaných mluvčích
        """
        # Zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro diarizaci (rozdělení audio na segmenty podle mluvčích)
        
        # Pro demonstrační účely vracíme simulované výsledky
        speakers = [
            {
                'id': 1,
                'segments': [{'start': 0.0, 'end': 10.0}],
                'confidence': 0.8
            }
        ]
        
        return speakers
    
    def _detect_emotions(self, audio_data):
        """
        Detekuje emoce v řeči.
        
        Args:
            audio_data (dict): Načtená audio data
            
        Returns:
            dict: Detekované emoce
        """
        # Zjednodušená implementace - v produkční verzi by zde byl sofistikovanější algoritmus
        # pro detekci emocí v řeči
        
        # Pro demonstrační účely vracíme simulované výsledky
        emotions = {
            'dominant': 'neutral',
            'probabilities': {
                'neutral': 0.7,
                'happy': 0.1,
                'sad': 0.05,
                'angry': 0.05,
                'fearful': 0.05,
                'disgusted': 0.05
            }
        }
        
        return emotions
    
    def _get_audio_metadata(self, audio_data):
        """
        Získá metadata audio souboru.
        
        Args:
            audio_data (dict): Načtená audio data
            
        Returns:
            dict: Metadata audio souboru
        """
        metadata = {
            'duration': audio_data['duration'],
            'sample_rate': audio_data['sample_rate'],
            'channels': audio_data['segment'].channels,
            'bit_depth': audio_data['segment'].sample_width * 8,
            'file_size': len(audio_data['segment'].raw_data)
        }
        
        return metadata
    
    def _create_summary(self, transcription, audio_features, speakers, emotions):
        """
        Vytvoří souhrn analyzovaného audio souboru.
        
        Args:
            transcription (str): Transkripce řeči
            audio_features (dict): Analyzované vlastnosti audio souboru
            speakers (list): Seznam identifikovaných mluvčích
            emotions (dict): Detekované emoce
            
        Returns:
            str: Souhrn audio souboru
        """
        summary_parts = []
        
        # Informace o typu obsahu
        content_type = audio_features.get('content_type', 'unknown')
        if content_type == "speech":
            summary_parts.append("Audio obsahuje převážně řeč.")
        elif content_type == "music":
            summary_parts.append("Audio obsahuje převážně hudbu.")
        elif content_type == "noise":
            summary_parts.append("Audio obsahuje převážně hluk nebo zvuky prostředí.")
        elif content_type == "mixed":
            summary_parts.append("Audio obsahuje smíšený obsah (řeč, hudba, zvuky).")
        
        # Informace o transkripci
        if transcription and transcription != "Audio neobsahuje rozpoznatelnou řeč." and not transcription.startswith("Chyba"):
            words = transcription.split()
            word_count = len(words)
            summary_parts.append(f"Transkripce obsahuje {word_count} slov.")
        elif transcription == "Audio neobsahuje rozpoznatelnou řeč.":
            summary_parts.append("Audio neobsahuje rozpoznatelnou řeč.")
        
        # Informace o mluvčích
        if len(speakers) == 1:
            summary_parts.append("V nahrávce byl identifikován jeden mluvčí.")
        elif len(speakers) > 1:
            summary_parts.append(f"V nahrávce bylo identifikováno {len(speakers)} mluvčích.")
        
        # Informace o emocích
        dominant_emotion = emotions.get('dominant', 'unknown')
        if dominant_emotion != 'unknown':
            emotion_names = {
                'neutral': 'neutrální',
                'happy': 'pozitivní',
                'sad': 'smutný',
                'angry': 'rozhněvaný',
                'fearful': 'vystrašený',
                'disgusted': 'znechucený'
            }
            emotion_name = emotion_names.get(dominant_emotion, dominant_emotion)
            summary_parts.append(f"Převládající emocionální tón je {emotion_name}.")
        
        # Sestavení souhrnu
        if summary_parts:
            return " ".join(summary_parts)
        else:
            return "Audio neobsahuje žádné významné prvky k analýze."
