"""
Abstract file management interface for audio recording.
Provides file operations abstraction to decouple audio recording from file handling.
"""
import uuid
import shutil
from abc import ABC, abstractmethod
import os
import tempfile
import logging


class FileManager(ABC):
    """Abstract interface for file management operations."""
    
    @abstractmethod
    def create_temp_file(self, suffix: str = '.wav', prefix: str = 'audio_') -> str:
        """Create a temporary file and return its path."""
        pass
    
    @abstractmethod
    def write_audio_data(self, file_path: str, audio_data, sample_rate: int, channels: int) -> bool:
        """Write audio data to file. Returns True on success."""
        pass
    
    @abstractmethod
    def cleanup_file(self, file_path: str) -> bool:
        """Remove a file. Returns True on success."""
        pass
    
    @abstractmethod
    def cleanup_temp_files(self) -> int:
        """Clean up temporary files for this instance."""
        pass

    def cleanup_temp_files(self) -> int:
        """Clean up all temporary files (with the prefix matching this app)."""
        pass


class TempFileManager(FileManager):
    """File manager that stores files in system temp directory."""
    
    def __init__(self):
        base_temp_dir = tempfile.gettempdir()
        random_subdir = f"mic_to_keyboard_{uuid.uuid4().hex}"
        self.temp_dir = os.path.join(base_temp_dir, random_subdir)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def create_temp_file(self, suffix: str = '.wav', prefix: str = 'audio_') -> str:
        """Create a temporary file and return its path."""
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix, 
            prefix=prefix, 
            dir=self.temp_dir
        )
        os.close(fd)
        return temp_path
    
    def write_audio_data(self, file_path: str, audio_data, sample_rate: int, channels: int) -> bool:
        """Write audio data to WAV file."""
        try:
            import soundfile as sf
            sf.write(file_path, audio_data, sample_rate)
            self.logger.info(f"Audio data written to: {file_path}")
            return True
        except ImportError:
            # Fallback to wave module if soundfile not available
            try:
                import wave
                import numpy as np
                
                # Convert to int16 if needed
                if audio_data.dtype != np.int16:
                    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                        audio_data = (audio_data * 32767).astype(np.int16)
                
                with wave.open(file_path, 'wb') as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(2)  # 2 bytes for int16
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                
                self.logger.info(f"Audio data written to: {file_path}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to write audio data: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to write audio data: {e}")
            return False
    
    def cleanup_file(self, file_path: str) -> bool:
        """Remove a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Cleaned up file: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to cleanup file {file_path}: {e}")
            return False
    
    def cleanup_temp_files(self) -> int:
        """Clean up all items in the temp directory."""
        count = 0
        try:
            import shutil
            for filename in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, filename)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        self.logger.info(f"Cleaned up file: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        self.logger.info(f"Cleaned up directory: {item_path}")
                    count += 1
                except Exception as e:
                    self.logger.error(f"Failed to cleanup {item_path}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
        
        return count

    def cleanup_all_temp_files(self) -> int:
        count = 0
        base_temp_dir = tempfile.gettempdir()
        prefix = "mic_to_keyboard"
        try:
            for name in os.listdir(base_temp_dir):
                if name.startswith(prefix):
                    dir_path = os.path.join(base_temp_dir, name)
                    try:
                        shutil.rmtree(dir_path)
                        self.logger.info(f"Removed temp directory: {dir_path}")
                        count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to remove temp directory {dir_path}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to cleanup all temp directories: {e}")
        return count
        


class CustomDirFileManager(TempFileManager):
    """File manager that stores files in a custom directory."""
    
    def __init__(self, directory: str):
        """Initialize with custom directory path."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        super().__init__(temp_dir=directory)