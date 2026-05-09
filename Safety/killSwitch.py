import keyboard
import os
import time

class KillSwitch:

    def __init__(self, hotkey="ctrl+shift+z"):
        self.hotkey = hotkey
        self.is_active = False
    
    def emergency_stop(self):
        print(f"\n[CRITICAL] Kill-switch triggered via '{self.hotkey}'!")
        print("[CRITICAL] Terminating Sentinel immediately...")
        self.disarm()
        os._exit(1)

    def arm(self):
        if not self.is_active:
            print(f"[Safety] Kill-switch armed. Emergency stop hotkey: '{self.hotkey}'")
            keyboard.add_hotkey(self.hotkey, self.emergency_stop)
            self.is_active = True

    def disarm(self):
        if self.is_active:
            keyboard.remove_hotkey(self.hotkey)
            self.is_active = False
            print(f"[Safety] Kill-switch disarmed.")