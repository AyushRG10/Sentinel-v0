import os
import signal

class KillSwitch:
    def __init__(self, panic_key: str = "z"):
        self.panic_key = panic_key.lower()
        self.is_armed = False

    def arm(self) -> None:
        if self.is_armed:
            return
        
        # We now catch SIGTSTP, which corresponds to Ctrl+Z
        signal.signal(signal.SIGTSTP, self._handle_signal)
        
        self.is_armed = True
        print(f"Sentinel: [INFO] Kill-switch armed. Press Ctrl+Z to exit.", flush=True)

    def _handle_signal(self, sig, frame):
        self._panic_trigger()

    def _panic_trigger(self) -> None:
        print("\nSentinel: [EMERGENCY] Kill-switch triggered. Exiting...", flush=True)
        os._exit(1)