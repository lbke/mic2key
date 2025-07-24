"""
Test audio recording functions for development and testing purposes.
"""
import numpy as np
import logging
from typing import Optional, Callable
import asyncio
from audio_recorder import AudioRecorder, AsyncAudioRecorder


class DummyAudioRecorder(AudioRecorder):
    """Audio recorder with test functions for development and testing."""
    
    def generate_test_audio(self, frequency: float = 440.0, duration: float = 1.0, 
                          amplitude: float = 0.5) -> np.ndarray:
        """
        Generate synthetic audio for testing.
        
        Args:
            frequency: Tone frequency in Hz (0 for silence)
            duration: Audio duration in seconds
            amplitude: Audio amplitude (0.0 to 1.0)
            
        Returns:
            NumPy array of audio samples
        """
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        
        if frequency > 0:
            audio_data = amplitude * np.sin(2 * np.pi * frequency * t)
        else:
            # Generate very low amplitude noise for silence
            audio_data = np.random.normal(0, amplitude * 0.01, samples)
        
        return audio_data.astype(np.float32)
    
    def record_test_audio(self, frequency: float = 440.0, duration: float = 1.0) -> Optional[str]:
        """
        Record synthetic test audio instead of from microphone.
        Useful for testing without audio hardware.
        
        Args:
            frequency: Test tone frequency in Hz
            duration: Audio duration in seconds
            
        Returns:
            Path to recorded test audio file or None on failure
        """
        audio_data = self.generate_test_audio(frequency, duration)
        return self._save_audio_data(audio_data)


class DummyAsyncAudioRecorder(AsyncAudioRecorder):
    """Asynchronous audio recorder with test functions."""
    
    def generate_test_audio(self, frequency: float = 440.0, duration: float = 1.0, 
                          amplitude: float = 0.5) -> np.ndarray:
        """
        Generate synthetic audio for testing.
        
        Args:
            frequency: Tone frequency in Hz (0 for silence)
            duration: Audio duration in seconds
            amplitude: Audio amplitude (0.0 to 1.0)
            
        Returns:
            NumPy array of audio samples
        """
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        
        if frequency > 0:
            audio_data = amplitude * np.sin(2 * np.pi * frequency * t)
        else:
            # Generate very low amplitude noise for silence
            audio_data = np.random.normal(0, amplitude * 0.01, samples)
        
        return audio_data.astype(np.float32)
    
    async def record_test_audio_async(self, frequency: float = 440.0, duration: float = 1.0,
                                    progress_callback: Optional[Callable[[float], None]] = None) -> Optional[str]:
        """
        Record synthetic test audio asynchronously.
        
        Args:
            frequency: Test tone frequency in Hz
            duration: Audio duration in seconds
            progress_callback: Optional progress callback
            
        Returns:
            Path to recorded test audio file or None on failure
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Generate test audio in executor
            audio_data = await loop.run_in_executor(
                None, self.generate_test_audio, frequency, duration
            )
            
            # Simulate progress if callback provided
            if progress_callback:
                steps = 10
                for i in range(steps + 1):
                    progress_callback(i / steps)
                    await asyncio.sleep(duration / steps / 10)  # Brief delay for simulation
            
            # Save audio data
            return await loop.run_in_executor(None, self._save_audio_data, audio_data)
            
        except Exception as e:
            self.logger.error(f"Failed to record test audio async: {e}")
            return None


# Convenience functions for creating test recorders
def create_dummy_recorder(sample_rate: int = 16000, channels: int = 1, 
                         file_manager=None) -> DummyAudioRecorder:
    """Create a synchronous dummy audio recorder for testing."""
    return DummyAudioRecorder(sample_rate, channels, file_manager)


def create_dummy_async_recorder(sample_rate: int = 16000, channels: int = 1,
                               file_manager=None) -> DummyAsyncAudioRecorder:
    """Create an asynchronous dummy audio recorder for testing."""
    return DummyAsyncAudioRecorder(sample_rate, channels, file_manager)