import requests
import json

class OllamaClient:

    def __init__ (self, host="http://localhost:11434", default_model="llama3.1:latest"):
        self.host = host
        self.default_model = default_model
        self.api_generate_url = f"{self.host}/api/generate"
        self.api_chat_url = f"{self.host}/api/chat"
        
        # Tool schemas for Obsidian memory
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_obsidian_note",
                    "description": "Searches the memory vault for a keyword and returns a list of matching file paths. You must use the read_obsidian_note tool on one of the resulting file paths to actually read the contents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "The keyword to search for."
                            }
                        },
                        "required": ["keyword"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_obsidian_note",
                    "description": "Reads the content of a specific note from the memory vault.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "note_path": {
                                "type": "string",
                                "description": "The relative path of the note to read, e.g., 'Rules\\Directives.md'"
                            }
                        },
                        "required": ["note_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_obsidian_note",
                    "description": "Appends content to a specific note in the memory vault.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "note_path": {
                                "type": "string",
                                "description": "The relative path of the note to write to."
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to append."
                            }
                        },
                        "required": ["note_path", "content"]
                    }
                }
            }
        ]

    def check_health(self):
        try:
            response = requests.get(self.host, timeout=3)

            if response.status_code == 200:
                return True
            return False

        except Exception as e:
            print(f"Error is: {e}")
            return False

    def generate_response(self, prompt_or_messages, model=None):
        target_model = model if model else self.default_model

        # If the user passes a simple string, convert it to a message format automatically!
        if isinstance(prompt_or_messages, str):
            messages = [{"role": "user", "content": prompt_or_messages}]
        else:
            messages = prompt_or_messages

        payload = {
            "model": target_model,
            "messages": messages,
            "tools": self.tools,
            "stream": False,
            "options": {
                "num_ctx": 4096
            }
        }

        try:
            response = requests.post(self.api_chat_url, json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()
            return data.get("message")
            
        except requests.exceptions.RequestException as e:
            print(f"Error in generate_response: {e}")
            return None