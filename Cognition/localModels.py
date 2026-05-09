import requests
import json

class OllamaClient:

    def __init__ (self, host="http://localhost:11434", default_model="gemma3:4b"):
        self.host = host
        self.default_model = default_model
        self.api_generate_url = f"{self.host}/api/generate"

    def check_health(self):
        try:
            response = requests.get(self.host, timeout=3)

            if response.status_code == 200:
                return True
            return False

        except Exception as e:
            print(f"Error is: {e}")
            return False

    def generate_response(self, prompt, model=None, system_prompt=None):
        """
        Sends a prompt to local Ollama model and retrieves response
        Args:
            prompt (str): The prompt to send to the model
            model (str, optional): The model to use. Defaults to self.default_model
            system_prompt (str, optional): The system prompt to use. Defaults to None
        Returns:
            str: The response from the model
            None: If the response could not be generated
        """
        target_model = model if model else self.default_model

        #payload structure ollama expects
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
        }

        #add system prompt later - through obsidian most likely

        #implement requests.post call here using self.api_generate_url and the payload
        #Parse the JSON response and return the actual string of text
        try:
            response = requests.post(self.api_generate_url, json=payload, timeout=90)

            response.raise_for_status()

            data = response.json()

            return data.get("response")

        except requests.exceptions.RequestException as e:
            print(f"Error is: {e}")
            return None