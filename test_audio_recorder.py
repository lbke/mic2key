"""
Comprehensive tests for the improved AudioRecorder.
"""
import unittest
import asyncio
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import time
from typing import Optional

from audio_recorder import AudioRecorder, AsyncAudioRecorder
from file_manager import TempFileManager, CustomDirFileManager


# TODO: move to a file specific to file manager
class TestFileManager(unittest.TestCase):
    """Test the file manager implementations."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = TempFileManager(self.temp_dir)
    
    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_temp_file(self):
        """Test temporary file creation."""
        file_path = self.file_manager.create_temp_file(suffix='.wav', prefix='test_')
        
        self.assertTrue(file_path.startswith(self.temp_dir))
        self.assertTrue(file_path.endswith('.wav'))
        self.assertIn('test_', file_path)
        self.assertTrue(os.path.exists(file_path))
    
    def test_write_audio_data(self):
        """Test writing audio data to file."""
        file_path = self.file_manager.create_temp_file()
        sample_rate = 16000
        channels = 1
        
        # Create synthetic audio data
        duration = 1.0  # 1 second
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
        
        success = self.file_manager.write_audio_data(file_path, audio_data, sample_rate, channels)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(file_path))
        self.assertGreater(os.path.getsize(file_path), 0)
    
    def test_cleanup_file(self):
        """Test file cleanup."""
        file_path = self.file_manager.create_temp_file()
        self.assertTrue(os.path.exists(file_path))
        
        success = self.file_manager.cleanup_file(file_path)
        
        self.assertTrue(success)
        self.assertFalse(os.path.exists(file_path))
    
    def test_cleanup_temp_files(self):
        """Test bulk cleanup of temp files."""
        # Create multiple temp files
        files = []
        for i in range(3):
            file_path = self.file_manager.create_temp_file(prefix=f'cleanup_test_{i}_')
            files.append(file_path)
        
        count = self.file_manager.cleanup_temp_files('cleanup_test_')
        
        self.assertEqual(count, 3)
        for file_path in files:
            self.assertFalse(os.path.exists(file_path))


class TestAudioRecorder(unittest.TestCase):
    """Test the synchronous AudioRecorder."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = TempFileManager(self.temp_dir)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sounddevice.rec')
    @patch('sounddevice.wait')
    def test_record_audio_success(self, mock_wait, mock_rec):
        """Test successful audio recording."""
        # Mock audio data
        sample_rate = 16000
        duration = 2.0
        mock_audio_data = np.random.normal(0, 0.1, int(sample_rate * duration)).astype(np.float32)
        mock_rec.return_value = mock_audio_data
        
        recorder = AudioRecorder(
            sample_rate=sample_rate,
            file_manager=self.file_manager
        )
        
        file_path = recorder.record_audio(duration)
        
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))
        mock_rec.assert_called_once()
        mock_wait.assert_called_once()
    
    @patch('sounddevice.rec')
    def test_record_audio_failure(self, mock_rec):
        """Test audio recording failure handling."""
        mock_rec.side_effect = Exception("Audio device error")
        
        recorder = AudioRecorder(file_manager=self.file_manager)
        
        file_path = recorder.record_audio(1.0)
        
        self.assertIsNone(file_path)
    
    def test_generate_test_audio(self):
        """Test synthetic audio generation for testing."""
        recorder = AudioRecorder(file_manager=self.file_manager)
        
        audio_data = recorder.generate_test_audio(frequency=440, duration=1.0)
        
        self.assertIsInstance(audio_data, np.ndarray)
        self.assertEqual(len(audio_data), recorder.sample_rate)
        self.assertTrue(np.all(np.abs(audio_data) <= 1.0))
    
    def test_record_test_audio(self):
        """Test recording with synthetic audio data."""
        recorder = AudioRecorder(file_manager=self.file_manager)
        
        file_path = recorder.record_test_audio(frequency=440, duration=1.0)
        
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))
        self.assertGreater(os.path.getsize(file_path), 0)


class TestAsyncAudioRecorder(unittest.IsolatedAsyncioTestCase):
    """Test the asynchronous AudioRecorder."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = TempFileManager(self.temp_dir)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sounddevice.rec')
    @patch('sounddevice.wait')
    async def test_async_record_audio_success(self, mock_wait, mock_rec):
        """Test successful async audio recording."""
        sample_rate = 16000
        duration = 2.0
        mock_audio_data = np.random.normal(0, 0.1, int(sample_rate * duration)).astype(np.float32)
        mock_rec.return_value = mock_audio_data
        
        recorder = AsyncAudioRecorder(
            sample_rate=sample_rate,
            file_manager=self.file_manager
        )
        
        file_path = await recorder.record_audio_async(duration)
        
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))
    
    async def test_concurrent_recordings(self):
        """Test multiple concurrent recordings."""
        recorder = AsyncAudioRecorder(file_manager=self.file_manager)
        
        # Start multiple test recordings concurrently
        tasks = [
            recorder.record_test_audio_async(frequency=220 + i * 110, duration=0.5)
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All recordings should succeed
        for file_path in results:
            self.assertIsNotNone(file_path)
            self.assertTrue(os.path.exists(file_path))
    
    async def test_record_with_callback(self):
        """Test recording with progress callback."""
        callback_calls = []
        
        def progress_callback(progress: float):
            callback_calls.append(progress)
        
        recorder = AsyncAudioRecorder(file_manager=self.file_manager)
        
        file_path = await recorder.record_test_audio_async(
            duration=1.0,
            progress_callback=progress_callback
        )
        
        self.assertIsNotNone(file_path)
        self.assertGreater(len(callback_calls), 0)
        self.assertAlmostEqual(callback_calls[-1], 1.0, places=1)


class TestAudioQuality(unittest.TestCase):
    """Test audio quality and format handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = TempFileManager(self.temp_dir)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_audio_format_validation(self):
        """Test that generated audio has correct format."""
        recorder = AudioRecorder(
            sample_rate=44100,
            channels=2,
            file_manager=self.file_manager
        )
        
        audio_data = recorder.generate_test_audio(duration=1.0)
        
        # Check audio properties
        self.assertEqual(len(audio_data), 44100)  # 1 second at 44.1kHz
        self.assertTrue(audio_data.dtype in [np.float32, np.float64])
        self.assertTrue(np.all(np.abs(audio_data) <= 1.0))  # Normalized
    
    def test_different_sample_rates(self):
        """Test recording with different sample rates."""
        sample_rates = [8000, 16000, 22050, 44100, 48000]
        
        for rate in sample_rates:
            with self.subTest(sample_rate=rate):
                recorder = AudioRecorder(
                    sample_rate=rate,
                    file_manager=self.file_manager
                )
                
                audio_data = recorder.generate_test_audio(duration=0.5)
                expected_length = int(rate * 0.5)
                
                self.assertEqual(len(audio_data), expected_length)
    
    def test_noise_floor(self):
        """Test that silence generates appropriate noise floor."""
        recorder = AudioRecorder(file_manager=self.file_manager)
        
        # Generate very quiet audio (simulating background noise)
        audio_data = recorder.generate_test_audio(frequency=0, duration=1.0, amplitude=0.001)
        
        # Should be very quiet but not exactly zero (due to numerical precision)
        rms = np.sqrt(np.mean(audio_data**2))
        self.assertLess(rms, 0.01)


class MockAudioDevice:
    """Mock audio device for testing without hardware."""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        
    def generate_mock_audio(self, duration: float) -> np.ndarray:
        """Generate mock audio data."""
        samples = int(self.sample_rate * duration)
        # Generate a mix of sine waves to simulate speech-like audio
        t = np.linspace(0, duration, samples)
        audio = (
            0.3 * np.sin(2 * np.pi * 200 * t) +  # Low frequency
            0.2 * np.sin(2 * np.pi * 800 * t) +  # Mid frequency  
            0.1 * np.sin(2 * np.pi * 2000 * t)   # High frequency
        )
        # Add some noise
        noise = np.random.normal(0, 0.05, samples)
        return (audio + noise).astype(np.float32)


if __name__ == '__main__':
    unittest.main()