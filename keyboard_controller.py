from pynput.keyboard import Controller, Key
import logging
import time

class KeyboardController:
    def __init__(self, typing_delay: float = 0.01):
        self.controller = Controller()
        self.typing_delay = typing_delay
        self.logger = logging.getLogger(__name__)
        
    def type_text(self, text: str) -> bool:
        if not text or not text.strip():
            self.logger.warning("Empty text provided for typing")
            return False
            
        try:
            # Add a small delay before typing to ensure the target application is ready
            time.sleep(0.1)
            
            # Type the transcribed text
            cleaned_text = text.strip()
            self.controller.type(cleaned_text)
            
            # Add a space after the transcribed text
            self.controller.type(" ")
            
            self.logger.info(f"Successfully typed text: '{cleaned_text}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to type text: {e}")
            return False
    
    def send_key(self, key) -> bool:
        try:
            self.controller.press(key)
            self.controller.release(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send key {key}: {e}")
            return False