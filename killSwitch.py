import sys
import os
import time
import select
import termios
import threading

class KillSwitch:
    def __init__(self, panic_key: str = "x"):
        self.panic_key = panic_key.lower()
        self._thread = None
        self._stop_event = threading.Event()
        self.is_armed = False

    def arm(self) -> None:
        if self.is_armed:
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_stdin, daemon=True)
        self._thread.start()
        self.is_armed = True
        print(f"\n[INFO] Kill-switch armed. Press Ctrl+{self.panic_key.upper()} to exit.", flush=True)

    def _watch_stdin(self) -> None:
        target_byte = bytes([ord(self.panic_key) - 96])
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            new_settings = termios.tcgetattr(fd)
            
            new_settings[0] = new_settings[0] & ~termios.IXON
            
            new_settings[3] = new_settings[3] & ~termios.ICANON
            
            new_settings[3] = new_settings[3] | termios.OPOST
            
            termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            
            while not self._stop_event.is_set():
                ready, _, _ = select.select([fd], [], [], 0.1)
                if ready:
                    ch = os.read(fd, 1)
                    if ch == target_byte:
                        self._panic_trigger()
                        break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _panic_trigger(self) -> None:
        print("\n[EMERGENCY] Kill-switch triggered. Exiting...", flush=True)
        os._exit(1)