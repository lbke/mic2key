"""
Pyaudio is not maintained anymore, using python-sounddevice instead.
"""
import sounddevice as sd
import numpy as np
import asyncio
import logging
from typing import Optional, Callable
from file_manager import FileManager
import threading


class AudioRecorder:
    """Synchronous audio recorder using python-sounddevice.
    Will store files based on file_manager option,
    will use a temporary files manager as a default ('/tmp' folder)
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 file_manager: FileManager = None,
                 max_duration: Optional[float] = None):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            file_manager: File management interface (defaults to TempFileManager)
            max_duration: Maximum recording duration in seconds (optional)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.file_manager = file_manager
        self.max_duration = max_duration
        self.logger = logging.getLogger(__name__)
        
        # Recording state
        self._is_recording = False
        self._recording_thread = None
        self._audio_data = None
        self._stop_event = threading.Event()
        
        # Set sounddevice defaults
        sd.default.samplerate = sample_rate
        sd.default.channels = channels
    
    def start_recording(self) -> bool:
        """
        Start audio recording.
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self._is_recording:
            self.logger.warning("Recording already in progress")
            return False
            
        try:
            self.logger.info("Starting recording")
            self._is_recording = True
            self._stop_event.clear()
            self._audio_data = []
            
            # Start recording in a separate thread
            self._recording_thread = threading.Thread(target=self._record_continuously)
            self._recording_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            self._is_recording = False
            return False
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop audio recording and save to file.
        
        Returns:
            Path to recorded audio file or None on failure
        """
        if not self._is_recording:
            self.logger.warning("No recording in progress")
            return None
            
        try:
            self.logger.info("Stopping recording")
            self._stop_event.set()
            self._is_recording = False
            
            # Wait for recording thread to finish
            if self._recording_thread:
                self._recording_thread.join()
            
            # Concatenate all recorded chunks
            if self._audio_data:
                audio_data = np.concatenate(self._audio_data, axis=0)
                
                # Flatten if mono
                if self.channels == 1:
                    audio_data = audio_data.flatten()
                
                return self._save_audio_data(audio_data)
            else:
                self.logger.warning("No audio data recorded")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return None
    
    def _record_continuously(self):
        """Continuously record audio until stop event is set."""
        chunk_duration = 0.1  # 100ms chunks
        chunk_frames = int(chunk_duration * self.sample_rate)
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=chunk_frames
            ) as stream:
                while not self._stop_event.is_set():
                    # Read a chunk of audio
                    audio_chunk, overflowed = stream.read(chunk_frames)
                    
                    if overflowed:
                        self.logger.warning("Audio input overflow detected")
                    
                    # Apply max_duration limit if set
                    total_duration = len(self._audio_data) * chunk_duration
                    if self.max_duration and total_duration >= self.max_duration:
                        self.logger.warning(f"Maximum duration {self.max_duration}s reached")
                        break
                    
                    self._audio_data.append(audio_chunk)
                    
        except Exception as e:
            self.logger.error(f"Error in continuous recording: {e}")
            self._is_recording = False
    
    
    def _save_audio_data(self, audio_data: np.ndarray) -> Optional[str]:
        """Save audio data to file using file manager."""
        try:
            # Create temporary file
            file_path = self.file_manager.create_temp_file(suffix='.wav', prefix='audio_')
            
            # Write audio data
            success = self.file_manager.write_audio_data(
                file_path, audio_data, self.sample_rate, self.channels
            )
            
            if success:
                self.logger.info(f"Audio saved to: {file_path}")
                return file_path
            else:
                self.logger.error("Failed to write audio data")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to save audio data: {e}")
            return None

class AsyncAudioRecorder(AudioRecorder):
    """Asynchronous audio recorder for non-blocking operations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_task = None
        self._progress_callback = None
    
    async def start_recording(self, progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        """
        Start audio recording asynchronously.
        
        Args:
            progress_callback: Optional callback for recording progress (0.0 to 1.0)
            
        Returns:
            True if recording started successfully, False otherwise
        """
        if self._is_recording:
            self.logger.warning("Recording already in progress")
            return False
            
        try:
            self.logger.info("Starting async recording")
            self._is_recording = True
            self._stop_event.clear()
            self._audio_data = []
            self._progress_callback = progress_callback
            
            # Start recording task
            self._async_task = asyncio.create_task(self._record_continuously_async())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start async recording: {e}")
            self._is_recording = False
            return False
    
    async def stop_recording(self) -> Optional[str]:
        """
        Stop audio recording and save to file asynchronously.
        
        Returns:
            Path to recorded audio file or None on failure
        """
        if not self._is_recording:
            self.logger.warning("No recording in progress")
            return None
            
        try:
            self.logger.info("Stopping async recording")
            self._stop_event.set()
            self._is_recording = False
            
            # Wait for recording task to finish
            if self._async_task:
                await self._async_task
            
            # Concatenate all recorded chunks
            if self._audio_data:
                audio_data = np.concatenate(self._audio_data, axis=0)
                
                # Flatten if mono
                if self.channels == 1:
                    audio_data = audio_data.flatten()
                
                # Save audio data in executor to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self._save_audio_data, audio_data)
            else:
                self.logger.warning("No audio data recorded")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to stop async recording: {e}")
            return None
    
    async def _record_continuously_async(self):
        """Continuously record audio until stop event is set, with async progress reporting."""
        chunk_duration = 0.1  # 100ms chunks
        chunk_frames = int(chunk_duration * self.sample_rate)
        start_time = asyncio.get_event_loop().time()
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=chunk_frames
            ) as stream:
                while not self._stop_event.is_set():
                    # Read a chunk of audio
                    audio_chunk, overflowed = stream.read(chunk_frames)
                    
                    if overflowed:
                        self.logger.warning("Audio input overflow detected")
                    
                    # Apply max_duration limit if set
                    total_duration = len(self._audio_data) * chunk_duration
                    if self.max_duration and total_duration >= self.max_duration:
                        self.logger.warning(f"Maximum duration {self.max_duration}s reached")
                        break
                    
                    self._audio_data.append(audio_chunk)
                    
                    # Report progress if callback provided
                    if self._progress_callback:
                        current_time = asyncio.get_event_loop().time()
                        elapsed = current_time - start_time
                        if self.max_duration:
                            progress = min(elapsed / self.max_duration, 1.0)
                        else:
                            progress = elapsed  # Continuous progress without limit
                        self._progress_callback(progress)
                    
                    # Yield control to event loop
                    await asyncio.sleep(0)
                    
        except Exception as e:
            self.logger.error(f"Error in async continuous recording: {e}")
            self._is_recording = False


# Convenience functions for backward compatibility
def create_recorder(sample_rate: int = 16000, channels: int = 1, 
                   file_manager: Optional[FileManager] = None) -> AudioRecorder:
    """Create a synchronous audio recorder."""
    return AudioRecorder(sample_rate, channels, file_manager)


def create_async_recorder(sample_rate: int = 16000, channels: int = 1,
                         file_manager: Optional[FileManager] = None) -> AsyncAudioRecorder:
    """Create an asynchronous audio recorder."""
    return AsyncAudioRecorder(sample_rate, channels, file_manager)