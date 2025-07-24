# Code Generation Prompt: Voice-to-Keyboard Input System

## Project Overview
Create a Python-based voice input system for Ubuntu that uses OpenAI's Whisper for offline speech-to-text transcription. The system should run continuously in the background and be controlled via keyboard shortcuts.
The system is used on Ubuntu, which doesn't have a built-in voice input system.

## Core Requirements

### Functionality
- **Toggle Recording**: Use `Ctrl+Shift+Space` as hotkey to start/stop audio recording
- **Speech Recognition**: Use OpenAI Whisper for offline transcription (default model: "base")
- **Keyboard Simulation**: Type transcribed text at current cursor position using reliable library.
- **Background Operation**: Run as a continuous script (no GUI, terminate when script stops)
- **Cross-Application**: Work in any text input field across Ubuntu applications, by simulating keyboard events.

### Technical Specifications

#### Audio Handling
- **Sample Rate**: 16kHz
- **Channels**: Mono
- **Format**: 32-bit float
- **Recording Method**: Toggle-based (press once to start, again to stop)
- **Max Duration**: 30 seconds (auto-stop if hotkey not pressed)
- **Library**: Use `pyaudio` for audio capture.

#### Speech Recognition
- **Engine**: OpenAI Whisper
- **Model**: "base" (configurable)
- **Processing**: Offline, local transcription
- **Library**: `openai-whisper`

#### Keyboard Simulation
- **Library**: `pynput` for cross-platform keyboard control
- **Method**: Simulate typing at current cursor position
- **Behavior**: Type transcribed text followed by a space

#### Hotkey Detection
- **Combination**: `Ctrl+Shift+Space`
- **Detection**: Global hotkey listener (works when app not in focus)
- **Library**: `pynput` for global hotkey detection

## Implementation Requirements

Use Python.

### Main Script Structure

```
voice_input.py
├── VoiceInputSystem class
├── Audio recording management
├── Whisper transcription
├── Keyboard simulation
├── Global hotkey listener
└── Main execution loop
```

Structure the code so that each problem is solved in a different file. This will make it easier to test different solutions.

### Key Components to Implement

1. **VoiceInputSystem Class** : the main class that uses other classes
   - Initialize Whisper model
   - Set up audio recording parameters
   - Create keyboard controller instance
   - Manage recording state (idle/recording/processing)
   - On startup, delete previous recording to preserve user's privacy.
   - On exit, gracefully delete recordings to preserve user's privacy.

2. **Audio Recording Manager**
   - Toggle recording on hotkey press
   - Capture audio data in memory
   - Handle recording timeout (30 seconds max)
   - Convert audio format for Whisper compatibility

3. **Transcription Handler**
   - Process recorded audio with Whisper
   - Handle transcription errors gracefully
   - Return cleaned text (strip whitespace, handle empty results)
   - Delete audio to preserver user's privacy.

4. **Keyboard Controller**
   - Type transcribed text at cursor position
   - Add space after each transcription
   - Handle special characters and unicode properly

5. **Global Hotkey Listener**
   - Listen for `Ctrl+Shift+Space` globally
   - Toggle recording state
   - Provide visual/audio feedback (optional beep or console message)

### Error Handling
- Graceful handling of audio device errors
- Whisper model loading failures
- Empty or failed transcriptions
- Keyboard permission issues
- Microphone access problems

### Configuration
- Whisper model size selection
- Max recording duration limit (to avoid forgetting to stop recording)
- Audio device selection
- Hotkey customization
- Debug mode toggle

All paramters are done through CLI parameters, with sensible defaults.

## Code Requirements

### Dependencies
```python
import whisper
import pyaudio
import numpy as np
import pynput.keyboard as keyboard
import threading
import time
import sys
import logging
```

### Expected Behavior
1. Script starts and loads Whisper model
2. Prints "Voice input system ready. Press Ctrl+Shift+Space to start/stop recording."
3. Waits for hotkey press
4. On first hotkey: Start recording, print "Recording started..."
5. On second hotkey: Stop recording, print "Processing...", transcribe, type result
6. Repeat cycle until script termination

### Performance Considerations
- Load Whisper model once at startup
- Use threading for non-blocking audio recording
- Minimal memory usage for audio buffering
- Fast transcription processing (< 3 seconds for short clips)

### Platform Compatibility
- Target: Ubuntu 20.04+ (primary)
- Python: 3.8+
- Audio: PulseAudio/ALSA compatible
- Permissions: Standard user permissions (no root required)

## File Structure to Generate
```
voice_input.py          # Main script
requirements.txt        # Python dependencies
config.py              # Configuration options (optional)
# Other code file to get a proper system
```

## Additional Notes
- Include comprehensive error handling and logging
- Add command-line arguments for debug mode and model selection
- Ensure clean shutdown on Ctrl+C
- Include helpful console output for user feedback
- Test with various microphone qualities and background noise levels
- Handle edge cases like very short recordings or silence

## Success Criteria
The generated code should:
1. Run without errors on a fresh Ubuntu installation
2. Respond to the specified hotkey combination
3. Record audio when hotkey is pressed
4. Stop recording and transcribe when hotkey is pressed again
5. Type the transcribed text in the currently focused application
6. Handle errors gracefully without crashing
7. Provide clear console feedback about system state

Generate clean, well-documented Python code that implements this voice input system according to these specifications.
