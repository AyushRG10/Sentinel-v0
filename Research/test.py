from Cognition.brain import OllamaClient

client = OllamaClient()

if client.check_health():
    print("Sentinel: Core systems are online.")

    response = client.generate_response("Hello, how are you?")
    if response:
        print(f"Sentinel: {response}")
    else:
        print("Sentinel: Failed to get a response.")
else:
    print("Sentinel: Initialization failed. Start Ollama.")