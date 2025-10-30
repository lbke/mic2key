import whisper
import logging
import os
from typing import Optional

class TranscriptionHandler:
    def __init__(self, model_name: str = "base", language: str = "en"):
        self.model_name = model_name
        self.language = language
        self.model: Optional[whisper.Whisper] = None
        self.logger = logging.getLogger(__name__)
        
    def load_model(self) -> bool:
        try:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self.logger.info("Whisper model loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            return False
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        if not self.model:
            self.logger.error("Whisper model not loaded")
            return None
            
        if not os.path.exists(audio_file_path):
            self.logger.error(f"Audio file not found: {audio_file_path}")
            return None
            
        try:
            self.logger.info(f"Starting transcription (language: {self.language})...")
            result = self.model.transcribe(audio_file_path, language=self.language)
            
            transcribed_text = result.get("text", "").strip()
            
            if not transcribed_text:
                self.logger.warning("Transcription resulted in empty text")
                return None
                
            self.logger.info(f"Transcription completed: '{transcribed_text}'")
            return transcribed_text
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return None
        finally:
            # Clean up the audio file for privacy
            try:
                if os.path.exists(audio_file_path):
                    os.remove(audio_file_path)
                    self.logger.info(f"Audio file deleted for privacy: {audio_file_path}")
            except Exception as e:
                self.logger.error(f"Failed to delete audio file: {e}")
    
    def is_model_loaded(self) -> bool:
        return self.model is not None