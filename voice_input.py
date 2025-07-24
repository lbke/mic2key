#!/usr/bin/env python3

from file_manager import TempFileManager

import argparse
import logging
import signal
import sys
import time
from enum import Enum

from audio_recorder import AudioRecorder
from transcription_handler import TranscriptionHandler
from keyboard_controller import KeyboardController
from hotkey_listener import HotkeyListener

class SystemState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"

class VoiceInputSystem:
    def __init__(self, 
                 whisper_model: str = "base",
                 max_recording_duration: int = 30,
                 debug: bool = False):
        
        self.state = SystemState.IDLE
        self.debug = debug
        
        # Initialize components
        self.file_manager = TempFileManager()
        self.audio_recorder = AudioRecorder(max_duration=max_recording_duration, file_manager=self.file_manager)
        self.transcription_handler = TranscriptionHandler(model_name=whisper_model)
        self.keyboard_controller = KeyboardController()
        self.hotkey_listener = HotkeyListener(self._on_hotkey_pressed)
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Flag for graceful shutdown
        self.running = True
        # Setup signal handlers for cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def initialize(self) -> bool:
        self.logger.info("Initializing Voice Input System...")
        
        # Clean up any old temporary files
        self.file_manager.cleanup_temp_files()
        
        # Load Whisper model
        if not self.transcription_handler.load_model():
            self.logger.error("Failed to load Whisper model")
            return False
        
        # Start hotkey listener
        if not self.hotkey_listener.start_listening():
            self.logger.error("Failed to start hotkey listener")
            return False
        
        self.logger.info("Voice input system ready. Press Ctrl+Shift+Space to start/stop recording.")
        return True
    
    def _on_hotkey_pressed(self):
        if self.state == SystemState.IDLE:
            self._start_recording()
        elif self.state == SystemState.RECORDING:
            self._stop_recording_and_process()
        else:
            self.logger.warning(f"Hotkey pressed while in {self.state.value} state - ignoring")
    
    def _start_recording(self):
        self.logger.info("Recording started...")
        print("Recording started...")
        
        if self.audio_recorder.start_recording():
            self.state = SystemState.RECORDING
        else:
            self.logger.error("Failed to start recording")
            print("Failed to start recording")
    
    def _stop_recording_and_process(self):
        self.logger.info("Processing...")
        print("Processing...")
        
        self.state = SystemState.PROCESSING
        
        # Stop recording and get audio file
        audio_file = self.audio_recorder.stop_recording()
        
        if not audio_file:
            self.logger.warning("No audio file generated")
            print("No audio recorded")
            self.state = SystemState.IDLE
            return
        
        # Transcribe audio
        transcribed_text = self.transcription_handler.transcribe_audio(audio_file)
        
        if transcribed_text:
            self.logger.info(f"Transcribed: '{transcribed_text}'")
            print(f"Transcribed: '{transcribed_text}'")
            
            # Type the transcribed text
            if self.keyboard_controller.type_text(transcribed_text):
                self.logger.info("Text typed successfully")
            else:
                self.logger.error("Failed to type text")
                print("Failed to type text")
        else:
            self.logger.warning("Transcription failed or resulted in empty text")
            print("Could not transcribe audio")
        
        self.state = SystemState.IDLE
        self.logger.info("Ready for next recording")
    
    def run(self):
        if not self.initialize():
            return False
        
        try:
            # Main loop - just wait for hotkey events
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()
        
        return True
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}")
        self.running = False
    
    def shutdown(self):
        self.logger.info("Shutting down Voice Input System...")
        
        # Stop hotkey listener
        if self.hotkey_listener:
            self.hotkey_listener.stop_listening()
        
        # Stop any ongoing recording
        if self.state == SystemState.RECORDING:
            self.audio_recorder.stop_recording()
        
        # Clean up temporary files
        self.file_manager.cleanup_temp_files()
        
        self.logger.info("Shutdown complete")

def main():
    parser = argparse.ArgumentParser(description="Voice-to-Keyboard Input System")
    parser.add_argument(
        "--model", 
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--max-duration",
        type=int,
        default=30,
        help="Maximum recording duration in seconds (default: 30)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Create and run the voice input system
    system = VoiceInputSystem(
        whisper_model=args.model,
        max_recording_duration=args.max_duration,
        debug=args.debug
    )
    
    success = system.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()