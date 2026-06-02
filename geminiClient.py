import json
import time
import urllib.request
import urllib.error
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

def _load_api_keys() -> list[str]:
    """Load all GEMINI_KEY_1 .. GEMINI_KEY_N from environment in order."""
    keys = []
    i = 1
    while True:
        key = os.getenv(f"GEMINI_KEY_{i}")
        if key is None:
            break
        keys.append(key)
        i += 1
    return keys

class OnlineLLMsClient:
    def __init__(self, api_key: str = ""):
        self.model = "gemini-2.5-flash"

        if api_key:
            # Caller supplied an explicit key — use it directly, no cycling.
            self._keys = [api_key]
            self._key_index = 0
        else:
            self._keys = _load_api_keys()
            if not self._keys:
                raise RuntimeError("Sentinel [ERROR]: No GEMINI_KEY_* variables found in environment.")
            # Find the first working key at startup.
            self._key_index = self._find_first_working_key()

        self.api_key = self._keys[self._key_index]
        print(f"Sentinel [INFO]: Using GEMINI_KEY_{self._key_index + 1} as active API key.")

    def _build_url(self, key: str) -> str:
        return BASE_URL.format(model=self.model, key=key)

    def _is_quota_error(self, exc: urllib.error.HTTPError) -> bool:
        return exc.code in (429, 403)

    def _find_first_working_key(self) -> int:
        """
        Probe each key with a minimal request starting from index 0.
        Returns the index of the first key that does not return a quota error.
        """
        probe_payload = json.dumps({
            "contents": [{"parts": [{"text": "hi"}]}]
        }).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        for idx, key in enumerate(self._keys):
            url = self._build_url(key)
            req = urllib.request.Request(url, data=probe_payload, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req):
                    print(f"Sentinel [INFO]: GEMINI_KEY_{idx + 1} is available.")
                    return idx
            except urllib.error.HTTPError as e:
                if self._is_quota_error(e):
                    print(f"Sentinel [WARNING]: GEMINI_KEY_{idx + 1} is rate-limited, trying next key...")
                    continue
                # Non-quota HTTP error on first key — still use it (may be transient).
                print(f"Sentinel [WARNING]: GEMINI_KEY_{idx + 1} returned HTTP {e.code}, using it anyway.")
                return idx
            except urllib.error.URLError:
                # Network issue during probe — fall back to key 0 and let generate() handle it.
                print(f"Sentinel [WARNING]: Could not probe keys (network error). Defaulting to GEMINI_KEY_1.")
                return 0

        print(f"Sentinel [WARNING]: All {len(self._keys)} keys appear rate-limited. Starting from GEMINI_KEY_1.")
        return 0

    def _advance_key(self) -> bool:
        """
        Move to the next available key.
        Returns True if a new key was selected, False if all keys are exhausted.
        """
        next_index = self._key_index + 1
        if next_index >= len(self._keys):
            return False
        self._key_index = next_index
        self.api_key = self._keys[self._key_index]
        print(f"Sentinel [INFO]: Switched to GEMINI_KEY_{self._key_index + 1}.")
        return True

    def generate_response(self, prompt: str, system_instruction: str = "", use_grounding: bool = True) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        if use_grounding:
            payload["tools"] = [{"google_search": {}}]

        attempts = 5
        delays = [1, 2, 4, 8, 16]

        while True:
            url = self._build_url(self._keys[self._key_index])
            data_bytes = json.dumps(payload).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

            for attempt in range(attempts):
                try:
                    with urllib.request.urlopen(req) as response:
                        res_body = response.read().decode("utf-8")
                        res_json = json.loads(res_body)

                        candidates = res_json.get("candidates")
                        if candidates and len(candidates) > 0:
                            content = candidates[0].get("content")
                            if content:
                                parts = content.get("parts")
                                if parts and len(parts) > 0:
                                    text = parts[0].get("text")
                                    if text is not None:
                                        return text

                        return "Error: Received empty or invalid response structure from API."

                except urllib.error.HTTPError as e:
                    if self._is_quota_error(e):
                        print(f"Sentinel [WARNING]: GEMINI_KEY_{self._key_index + 1} hit rate limit during request.")
                        if self._advance_key():
                            break  # Break inner retry loop → restart outer loop with new key.
                        else:
                            return "Sentinel [ERROR]: All API keys have been exhausted. Please try again later."
                    elif attempt < attempts - 1:
                        time.sleep(delays[attempt])
                    else:
                        return f"Sentinel [ERROR]: Request failed after {attempts} attempts. HTTP {e.code}: {str(e)}"

                except urllib.error.URLError as e:
                    if attempt < attempts - 1:
                        time.sleep(delays[attempt])
                    else:
                        return f"Sentinel [ERROR]: Online cognitive layer timed out/failed after {attempts} attempts. Error: {str(e)}"
            else:
                return "Sentinel [ERROR]: Online cognitive layer timed out after multiple attempts."