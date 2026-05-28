import json
import time
import urllib.request
import urllib.error
import os
from dotenv import load_dotenv
from google import genai
from genai import types

load_dotenv()

class OnlineLLMsClient:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("GEMINI_KEY_1")
        self.model = "gemini-2.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        data_bytes = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(self.url, data=data_bytes, headers=headers, method='POST')
        
        attempts = 5
        delays = [1, 2, 4, 8, 16]
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(req) as response:
                    res_body = response.read().decode('utf-8')
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
                    
            except urllib.error.URLError as e:
                if attempt < attempts - 1:
                    time.sleep(delays[attempt])
                else:
                    return f"Error: Online cognitive layer timed out/failed after {attempts} attempts. Error: {str(e)}"
        
        return "Error: Online cognitive layer timed out after multiple attempts."

if __name__ == "__main__":
    onlineClient = OnlineLLMsClient()
    print(onlineClient.generate_response("What is new about Antigravity 2.0?"))