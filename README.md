# Mic2key

A Python-based voice input system for Ubuntu that uses OpenAI's Whisper for offline speech-to-text transcription. The system runs continuously in the background and can be triggered with a keyboard shortcut.

**This project has been AI-generated with Claude Code and Cursor in a vibe coding approach.**
Human review is pending (07/2025), use at your own risk.

## Features

- **Offline Speech Recognition**: Uses OpenAI Whisper for local transcription
- **Multi-Language Support**: Supports 99+ languages including English, French, Spanish, German, and more
- **Keyboard Shortcut Control**: Press a hotkey to start/stop recording
- **Background Operation**: Runs as a system service/daemon. For now stick to running it a script, when the script is terminated transcription is done. The system has no user interface.
- **Cross-Application**: Works in any text input field. You need to send keyboard events using a reliable library.
- **Configurable**: Adjustable Whisper model size, recording settings, and language

## How It Works

1. The program runs continuously in the background
2. Press the configured hotkey (default: `Ctrl+Shift+<space>`) to start recording
3. Speak your message while the recording indicator is active
4. Press the hotkey again to stop recording and trigger transcription
5. The transcribed text is automatically typed at the current cursor position

## Installation

### Prerequisites

Install Python 3

This package requires `PortAudio`:

```sh
sudo apt-get update
# https://www.portaudio.com/
sudo apt-get install portaudio19-dev
```

The  recorder will output `OSError: PortAudio library not found` if you missed this step.

Alternatives: [`pyalsaaudio` for ALSA](https://github.com/larsimmisch/pyalsaaudio) doesn't seem to have been maintained lately. 

### Download and Setup

```bash
# Clone or download the project
git clone <repository-url>
cd mic-to-keyboard

# Install Python requirements
pip install -r requirements.txt

# Make the main script executable
chmod +x mic2key.py
```

## Configuration

### Whisper Model Selection

The system supports different Whisper model sizes. Choose based on your hardware capabilities:

- `tiny`: Fastest, least accurate (~39 MB)
- `base`: Good balance (~74 MB) - **Recommended**
- `small`: Better accuracy (~244 MB)
- `medium`: High accuracy (~769 MB)
- `large`: Best accuracy (~1550 MB)

### Language Selection

Use the `--language` parameter to specify your language:

- `en`: English (default)
- `fr`: French
- `es`: Spanish
- `de`: German
- `it`: Italian
- `pt`: Portuguese
- `ru`: Russian
- `ja`: Japanese
- `ko`: Korean
- `zh`: Chinese
- And many more...

Run `python3 mic2key.py --help` to see all supported languages.

### Keyboard Shortcut

Default hotkey is `Ctrl+Shift+V`. You can modify this in the configuration section of `mic2key.py`.

### Audio Settings

Default recording settings:
- Sample Rate: 16kHz
- Channels: Mono
- Format: 32-bit float
- Max recording duration: 30 seconds

## Usage

### Running the Program

```bash
# Run in foreground (for testing)
python3 mic2key.py

# Run with French language support
python3 mic2key.py --language fr

# Run with specific model and language
python3 mic2key.py --model base --language fr

# Run in background
python3 mic2key.py --language fr &

# Run as systemd service (recommended for permanent use)
sudo systemctl start voice-input
sudo systemctl enable voice-input  # Auto-start on boot
```

### Using Voice Input

1. **Start Recording**: Press `Ctrl+Shift+V`
   - You'll see a brief notification or hear a beep
   - Speak clearly into your microphone

2. **Stop Recording & Transcribe**: Press `Ctrl+Shift+V` again
   - Recording stops immediately
   - Transcription begins (may take 1-3 seconds)
   - Text is automatically typed at cursor position

### Example Workflow

```
1. Open any text editor (gedit, LibreOffice, browser, etc.)
2. Position cursor where you want text
3. Press Ctrl+Shift+V
4. Say: "Hello, this is a test of the voice input system."
5. Press Ctrl+Shift+V again
6. Watch as the text appears: "Hello, this is a test of the voice input system."
```

## Performance Tips

### For Better Accuracy
- Speak clearly and at normal pace
- Use a good quality microphone
- Minimize background noise
- Keep recordings under 15 seconds for faster processing

### For Better Performance
- Use `tiny` or `base` model for faster transcription
- Ensure sufficient RAM (2GB+ recommended for larger models)
- Close unnecessary applications during heavy usage

## System Integration

### Auto-Start on Login

Create a desktop entry:

```bash
# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart

# Create desktop entry
cat > ~/.config/autostart/voice-input.desktop << EOF
[Desktop Entry]
Type=Application
Name=Voice Input System
Exec=python3 /home/$USER/code/mic-to-keyboard/mic2key.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

### System Service (Advanced)

For system-wide availability, create a systemd service:

```bash
# Create service file
sudo tee /etc/systemd/system/voice-input.service << EOF
[Unit]
Description=Voice Input System
After=sound.target

[Service]
Type=simple
User=$USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /home/$USER/code/mic-to-keyboard/mic2key.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable voice-input.service
sudo systemctl start voice-input.service
```

## Troubleshooting

### Common Issues

**Microphone Not Detected**
```bash
# Check available audio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)}') for i in range(p.get_device_count())]"
```

**Permission Denied for Audio**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in
```

**Keyboard Input Not Working**
- Ensure the program has proper permissions for input simulation
- Some applications may block programmatic keyboard input

**High CPU Usage**
- Try using a smaller Whisper model (`tiny` or `base`)
- Reduce maximum recording duration
- Check for background processes consuming resources

### Debug Mode

Run with debug output:
```bash
python3 mic2key.py --debug
```

## Advanced Configuration

### Custom Hotkey

Edit `mic2key.py` and modify the hotkey configuration:

```python
# Change this line to customize your hotkey
HOTKEY = {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.KeyCode.from_char('v')}
```

### Recording Duration

Adjust maximum recording time:

```python
# In mic2key.py, modify this constant
MAX_RECORDING_DURATION = 30  # seconds
```

### Whisper Model Path

Specify custom model location:

```python
# Custom model path
MODEL_PATH = "/path/to/your/whisper/model"
model = whisper.load_model("base", download_root=MODEL_PATH)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- OpenAI for the Whisper speech recognition model
- PyAudio team for audio interface
- pynput developers for keyboard/mouse control
