import os
import sys
import tty
import time
import select
import termios
import threading

class KillSwitch:

    def __init__(self, panic_key: str = "q"):
        self.panic_key = panic_key.lower()
        self._thread = None
        self._stop_event = threading.Event()
        self.is_armed = False

    def arm(self) -> None:
        if self.is_armed:
            print("Sentinel: [INFO] Kill-switch already armed.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_stdin, daemon=True)
        self._thread.start()
        self.is_armed = True
        print(f"Sentinel: [INFO] Kill-switch armed. Press Ctrl+{self.panic_key.upper()} to exit.")

    def disarm(self) -> None:
        if not self.is_armed:
            print("Sentinel: [INFO] Kill-switch is not currently active.")
            return

        self._stop_event.set()
        self._thread = None
        self.is_armed = False
        print("Sentinel: [INFO] Kill-switch disarmed.")

    def _watch_stdin(self) -> None:
        # Ctrl+<key> sends ASCII: ord(key) - 96
        target_byte = bytes([ord(self.panic_key) - 96])
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            # setcbreak: disables canonical+echo, keeps OPOST (fixes staircase)
            # and keeps IXON (suppresses XON/XOFF bytes, fixes phantom trigger)
            tty.setcbreak(fd)
            while not self._stop_event.is_set():
                ready, _, _ = select.select([fd], [], [], 0.1)
                if ready:
                    ch = os.read(fd, 1)
                    if ch == target_byte:
                        self._panic_trigger()
        except Exception:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _panic_trigger(self) -> None:
        print("Sentinel: [EMERGENCY] Kill-switch triggered. Exiting...", flush=True)
        os._exit(1)


if __name__ == "__main__":
    kill_switch = KillSwitch()
    kill_switch.arm()

    while True:
        time.sleep(1)
        print("Sentinel: [INFO] Kill-switch is armed and waiting.")