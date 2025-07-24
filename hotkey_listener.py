from pynput import keyboard
import logging
from typing import Callable, Set

class HotkeyListener:
    def __init__(self, hotkey_callback: Callable[[], None]):
        self.hotkey_callback = hotkey_callback
        self.listener: keyboard.Listener = None
        self.pressed_keys: Set[keyboard.Key] = set()
        self.logger = logging.getLogger(__name__)
        
        # Define the hotkey combination: Ctrl+Shift+Space
        self.target_keys = {
            keyboard.Key.ctrl_l,  # Left Ctrl
            keyboard.Key.shift_l,  # Left Shift  
            keyboard.Key.space     # Space
        }
        
        # Also accept right Ctrl and Shift
        self.alt_target_keys = {
            keyboard.Key.ctrl_r,   # Right Ctrl
            keyboard.Key.shift_r,  # Right Shift
            keyboard.Key.space     # Space
        }
    
    def start_listening(self) -> bool:
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            self.logger.info("Hotkey listener started (Ctrl+Shift+Space)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
            return False
    
    def stop_listening(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.logger.info("Hotkey listener stopped")
    
    def _on_key_press(self, key):
        self.pressed_keys.add(key)
        
        # Check if hotkey combination is pressed
        if self._is_hotkey_pressed():
            self.logger.info("Hotkey combination detected")
            try:
                self.hotkey_callback()
            except Exception as e:
                self.logger.error(f"Error in hotkey callback: {e}")
    
    def _on_key_release(self, key):
        self.pressed_keys.discard(key)
    
    def _is_hotkey_pressed(self) -> bool:
        # Check if all keys in the target combination are pressed
        return (self.target_keys.issubset(self.pressed_keys) or 
                self.alt_target_keys.issubset(self.pressed_keys) or
                self._mixed_modifier_combination())
    
    def _mixed_modifier_combination(self) -> bool:
        # Allow mixed left/right modifiers
        has_ctrl = (keyboard.Key.ctrl_l in self.pressed_keys or 
                   keyboard.Key.ctrl_r in self.pressed_keys)
        has_shift = (keyboard.Key.shift_l in self.pressed_keys or 
                    keyboard.Key.shift_r in self.pressed_keys)
        has_space = keyboard.Key.space in self.pressed_keys
        
        return has_ctrl and has_shift and has_space
    
    def __del__(self):
        self.stop_listening()