import ollama
import socket

class OllamaClient:

    def check_model(self, host: str = "127.0.0.1", port: int = 11434) -> bool:

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def generate(self, model_name: str, prompt: str) -> str:
        
        try:
            kwargs = {
                "model": model_name,
                "prompt": prompt,
            }

            response = ollama.generate(**kwargs)
            return response.response
        except Exception as e:
            print(f"Error: {e}")
            return ""

if __name__ == "__main__":

    client = OllamaClient()

    isActive = client.check_model()
    if isActive:
        print("Sentinel: [RUNNING] Ollama is online.")

        while True:
            query = input("User: ")
            response = client.generate("llama3", query)
            print("Sentinel: ", response)
    else:
        print("Sentinel: [ERROR] Ollama is not running.")